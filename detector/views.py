import os
import glob
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .ml_model import predict_image
from .models import ScanRecord
from .pdf_generator import generate_clinical_pdf, CONDITION_INFO


def upload_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]

        try:
            pil_image = Image.open(uploaded_file)
            pil_image.verify()
            # Reopen after verify
            uploaded_file.seek(0)
            pil_image = Image.open(uploaded_file)
        except Exception:
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
        label, confidence, all_scores, gradcam_base64, urgency, trichometry, treatment = predict_image(pil_image)

        # Confidence threshold check
        CONFIDENCE_THRESHOLD = 50.0
        is_uncertain = confidence < CONFIDENCE_THRESHOLD

        # Persist scan to database
        scan_record = ScanRecord.objects.create(
            user=request.user if request.user.is_authenticated else None,
            image=uploaded_file,
            predicted_label=label,
            confidence=confidence,
            all_scores=all_scores,
            is_uncertain=is_uncertain,
        )

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


@login_required
def dashboard_view(request):
    scans = ScanRecord.objects.filter(user=request.user)
    total_scans = scans.count()
    conclusive_scans = scans.filter(is_uncertain=False).count()
    
    if total_scans > 0:
        avg_confidence = round(sum(s.confidence for s in scans) / total_scans, 1)
    else:
        avg_confidence = 0.0

    return render(
        request,
        "detector/dashboard.html",
        {
            "scans": scans,
            "total_scans": total_scans,
            "conclusive_scans": conclusive_scans,
            "avg_confidence": avg_confidence,
        },
    )


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
