import os
import glob
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .ml_model import predict_image
from .models import ScanRecord
from .pdf_generator import generate_clinical_pdf, CONDITION_INFO


def ping_view(request):
    return JsonResponse({"status": "ok", "service": "ScalpAI", "awake": True})


def upload_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]

        try:
            uploaded_file.seek(0)
            pil_image = Image.open(uploaded_file).convert("RGB")
        except Exception as e:
            print("Image open error:", e)
            return render(
                request,
                "detector/upload.html",
                {"error": "That file doesn't look like a valid image. Please try again."},
            )

        if not (settings.MODEL_PATH.exists() and settings.CLASS_NAMES_PATH.exists()):
            return render(
                request,
                "detector/upload.html",
                {
                    "error": (
                        "Model files not found. Please train or copy scalp_model.h5 "
                        "and class_names.json into django_app/model_files/ first."
                    )
                },
            )

        # Run EfficientNet-B0 prediction with TTA, Grad-CAM, Urgency, Trichometry, and Treatment Plan
        try:
            label, confidence, all_scores, gradcam_base64, urgency, trichometry, treatment = predict_image(pil_image)
        except Exception as e:
            print("Prediction error:", e)
            return render(
                request,
                "detector/upload.html",
                {"error": "An error occurred while analyzing the image. Please try uploading another photo."}
            )

        # Domain Guard Rejection: If photo is not scalp/hair related
        if label == "invalid_non_scalp_image":
            return render(
                request,
                "detector/upload.html",
                {
                    "error": "⚠️ Invalid Photo: The uploaded image does not appear to be a scalp or hair photograph. Please upload a clear close-up photo of the scalp or hair area."
                },
            )

        # Confidence threshold check
        CONFIDENCE_THRESHOLD = 50.0
        is_uncertain = confidence < CONFIDENCE_THRESHOLD

        # Convert pil_image to base64 for reliable display in result template
        import io
        import base64
        buf = io.BytesIO()
        pil_image.save(buf, format="JPEG", quality=85)
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Reset file pointer before saving to model ImageField
        uploaded_file.seek(0)

        # Persist scan to database (fallback safely if db error occurs)
        try:
            scan_record = ScanRecord.objects.create(
                user=request.user if request.user.is_authenticated else None,
                image=uploaded_file,
                predicted_label=label,
                confidence=confidence,
                all_scores=all_scores,
                is_uncertain=is_uncertain,
                trichometry_metrics=trichometry or {},
                urgency_tier=urgency.get("tier", "") if isinstance(urgency, dict) else "",
                urgency_badge=urgency.get("badge", "") if isinstance(urgency, dict) else "",
                treatment_summary=treatment or {},
                gradcam_base64=gradcam_base64 or "",
            )
            # If guest user, store scan id in session for automatic claiming upon login/register
            if not request.user.is_authenticated and scan_record:
                guest_scans = request.session.get("guest_scan_ids", [])
                guest_scans.append(scan_record.id)
                request.session["guest_scan_ids"] = guest_scans
                request.session.modified = True
        except Exception as e:
            print("ScanRecord creation notice:", e)
            scan_record = None

        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        cond_meta = CONDITION_INFO.get(label, {
            "title": label.replace("_", " ").title(),
            "desc": "A recognized condition affecting scalp tissue or hair follicle structures.",
            "advice": "Consult a certified medical dermatologist for clinical examination and management."
        })

        return render(
            request,
            "detector/result.html",
            {
                "scan_record": scan_record,
                "image_base64": image_base64,
                "label": cond_meta["title"],
                "confidence": confidence,
                "sorted_scores": sorted_scores,
                "is_uncertain": is_uncertain,
                "threshold": CONFIDENCE_THRESHOLD,
                "condition_desc": cond_meta["desc"],
                "condition_advice": cond_meta["advice"],
                "gradcam_base64": gradcam_base64,
                "urgency": urgency,
                "trichometry": trichometry,
                "treatment": treatment,
            },
        )

    return render(request, "detector/upload.html")


def download_pdf_view(request, scan_id):
    scan_record = get_object_or_404(ScanRecord, id=scan_id)
    patient_name = request.user.username if request.user.is_authenticated else "Guest Screening"
    
    pdf_bytes = generate_clinical_pdf(scan_record, patient_name=patient_name)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="ScalpAI_Report_#{scan_record.id:05d}.pdf"'
    return response


def scan_detail_view(request, scan_id):
    scan_record = get_object_or_404(ScanRecord, id=scan_id)

    # Authorization guard: allow if owned by user or created in current guest session
    is_owner = (request.user.is_authenticated and scan_record.user == request.user)
    is_guest_session = (scan_record.id in request.session.get("guest_scan_ids", []))
    if scan_record.user and not is_owner and not request.user.is_superuser:
        raise Http404("Scan record not found or access denied.")

    label = scan_record.predicted_label
    cond_meta = CONDITION_INFO.get(label, {
        "title": label.replace("_", " ").title(),
        "desc": "A recognized condition affecting scalp tissue or hair follicle structures.",
        "advice": "Consult a certified medical dermatologist for clinical examination and management."
    })

    sorted_scores = sorted(scan_record.all_scores.items(), key=lambda x: x[1], reverse=True) if scan_record.all_scores else []

    urgency = {
        "tier": scan_record.urgency_tier,
        "badge": scan_record.urgency_badge,
    }

    return render(
        request,
        "detector/scan_detail.html",
        {
            "scan_record": scan_record,
            "label": cond_meta["title"],
            "confidence": scan_record.confidence,
            "sorted_scores": sorted_scores,
            "is_uncertain": scan_record.is_uncertain,
            "threshold": 50.0,
            "condition_desc": cond_meta["desc"],
            "condition_advice": cond_meta["advice"],
            "gradcam_base64": scan_record.gradcam_base64,
            "urgency": urgency,
            "trichometry": scan_record.trichometry_metrics,
            "treatment": scan_record.treatment_summary,
        },
    )


@login_required
def dashboard_view(request):
    import json
    all_user_scans = ScanRecord.objects.filter(user=request.user)

    condition_filter = request.GET.get("condition", "").strip()
    search_query = request.GET.get("q", "").strip()

    scans = all_user_scans
    if condition_filter:
        scans = scans.filter(predicted_label__iexact=condition_filter)
    if search_query:
        scans = scans.filter(predicted_label__icontains=search_query)

    total_scans = all_user_scans.count()
    conclusive_scans = all_user_scans.filter(is_uncertain=False).count()
    avg_confidence = round(sum(s.confidence for s in all_user_scans) / total_scans, 1) if total_scans > 0 else 0.0

    # Build longitudinal recovery timeline dataset across user's chronological scans (oldest to newest)
    timeline_scans = list(all_user_scans.order_by("created_at")[:20])
    timeline_points = []
    for s in timeline_scans:
        metrics = s.trichometry_metrics or {}
        timeline_points.append({
            "id": s.id,
            "date": s.created_at.strftime("%b %d"),
            "health_score": float(metrics.get("health_score", 0.0) or 0.0),
            "erythema": float(metrics.get("erythema_pct", 0.0) or 0.0),
            "flakiness": float(metrics.get("flakiness_pct", 0.0) or 0.0),
            "label": s.predicted_label.replace("_", " ").title(),
        })

    user_conditions = sorted(list(set(all_user_scans.values_list("predicted_label", flat=True))))

    return render(
        request,
        "detector/dashboard.html",
        {
            "scans": scans,
            "total_scans": total_scans,
            "conclusive_scans": conclusive_scans,
            "avg_confidence": avg_confidence,
            "timeline_json": json.dumps(timeline_points),
            "has_timeline": len(timeline_points) >= 2,
            "user_conditions": user_conditions,
            "selected_condition": condition_filter,
            "search_query": search_query,
        },
    )


@login_required
def delete_scan_view(request, scan_id):
    if request.method != "POST":
        return redirect("dashboard")

    scan_record = get_object_or_404(ScanRecord, id=scan_id, user=request.user)
    if scan_record.image:
        try:
            if os.path.isfile(scan_record.image.path):
                os.remove(scan_record.image.path)
        except Exception as e:
            print("Media deletion note:", e)

    scan_record.delete()
    messages.success(request, f"Scan #{scan_id} was removed from your history.")
    return redirect("dashboard")


def sample_image_view(request, class_name):
    # Try external test set first, then train set
    search_paths = [
        os.path.join(settings.BASE_DIR, "..", "dataset", "external_test", class_name, "*.jpg"),
        os.path.join(settings.BASE_DIR, "..", "dataset", "train", class_name, "*.jpg"),
    ]
    for path_glob in search_paths:
        matches = glob.glob(path_glob)
        if matches:
            return FileResponse(open(matches[0], "rb"), content_type="image/jpeg")
    raise Http404("Sample image not found")


def claim_guest_scans(request, user):
    """
    Associates unauthenticated scans performed during the current session with the user.
    """
    guest_scan_ids = request.session.get("guest_scan_ids", [])
    if guest_scan_ids and user and user.is_authenticated:
        claimed_count = ScanRecord.objects.filter(id__in=guest_scan_ids, user__isnull=True).update(user=user)
        if claimed_count > 0:
            messages.info(request, f"Linked {claimed_count} previous scan{'s' if claimed_count > 1 else ''} to your account history.")
        request.session["guest_scan_ids"] = []
        request.session.modified = True


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif password != password_confirm:
            messages.error(request, "Passwords do not match. Please try again.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken. Please choose another.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            claim_guest_scans(request, user)
            messages.success(request, f"Welcome to ScalpAI, {username}!")
            return redirect("dashboard")

    return render(request, "detector/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            claim_guest_scans(request, user)
            messages.success(request, f"Welcome back, {username}!")
            next_url = request.GET.get("next") or "dashboard"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, "detector/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("upload")


def download_presentation_view(request):
    ppt_path = settings.BASE_DIR / "ScalpAI_Project_Presentation.pptx"
    if not ppt_path.exists():
        ppt_path = settings.BASE_DIR.parent / "ScalpAI_Project_Presentation.pptx"
    if ppt_path.exists():
        response = FileResponse(
            open(ppt_path, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        response["Content-Disposition"] = 'attachment; filename="ScalpAI_Project_Presentation.pptx"'
        return response
    raise Http404("Presentation file not found.")

