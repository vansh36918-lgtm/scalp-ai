import io
import os
import base64
import hashlib
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable, PageBreak
)

CONDITION_INFO = {
    "alopecia_areata": {
        "title": "Alopecia Areata",
        "desc": "An autoimmune condition causing round or oval patches of sudden, non-scarring hair loss. The body's immune system mistakenly attacks hair follicles.",
        "advice": "Consult a dermatologist. First-line treatments may include topical corticosteroids, minoxidil, or intralesional steroid injections."
    },
    "androgenetic_alopecia": {
        "title": "Androgenetic Alopecia",
        "desc": "Genetically predetermined progressive thinning and miniaturization of hair follicles (male or female pattern baldness).",
        "advice": "Evidence-based options include topical minoxidil, oral anti-androgens (under physician guidance), and low-level laser therapy."
    },
    "contact_dermatitis": {
        "title": "Contact Dermatitis",
        "desc": "An acute or subacute inflammatory reaction triggered by allergens or irritants (e.g. hair dyes, fragrances, surfactants) causing erythema and weeping.",
        "advice": "Identify and remove the offending allergen immediately. Cool compresses and topical mild corticosteroids can provide symptomatic relief."
    },
    "dandruff": {
        "title": "Dandruff (Pityriasis Capitis)",
        "desc": "Mild, non-inflammatory scalp shedding presenting as fine white or grayish dry flaking without marked erythema.",
        "advice": "Regular cleansing with over-the-counter anti-dandruff shampoos containing zinc pyrithione, ketoconazole, or selenium sulfide is recommended."
    },
    "folliculitis": {
        "title": "Folliculitis",
        "desc": "Superficial inflammation or bacterial/fungal infection of the hair follicles presenting as erythematous papules and pustules.",
        "advice": "Gentle antiseptic washes (e.g. chlorhexidine or benzoyl peroxide). Severe or persistent cases require targeted oral antibiotics or antifungals."
    },
    "folliculitis_decalvans": {
        "title": "Folliculitis Decalvans",
        "desc": "A chronic, cicatricial (scarring) alopecia characterized by tufted hairs ('doll's hairs'), recurrent follicular pustules, and irreversible hair loss.",
        "advice": "Requires urgent dermatological care to prevent permanent scarring. Long-term combination antibiotic therapy is commonly prescribed."
    },
    "lichen_planopilaris": {
        "title": "Lichen Planopilaris",
        "desc": "A primary cicatricial alopecia variant of lichen planus presenting with violaceous perifollicular erythema, keratotic spine casts, and follicular loss.",
        "advice": "Immediate evaluation by a trichology specialist. Anti-inflammatory treatments (corticosteroids, hydroxychloroquine) help halt scarring progression."
    },
    "normal_healthy_scalp": {
        "title": "Normal Healthy Scalp",
        "desc": "No evidence of pathological erythema, scaling, follicular plugging, or abnormal shedding. Hair density and follicular units appear physiological.",
        "advice": "Maintain standard scalp hygiene and balanced nutrition. No medical intervention required."
    },
    "pediculosis_capitis": {
        "title": "Pediculosis Capitis (Head Lice)",
        "desc": "Infestation by Pediculus humanus capitis with visible oval nits firmly cemented to hair shafts, accompanied by pruritus.",
        "advice": "Pediculicide treatments (e.g. permethrin or dimethicone-based lotions) combined with meticulous wet-combing with a fine-toothed nit comb."
    },
    "psoriasis": {
        "title": "Scalp Psoriasis",
        "desc": "A chronic autoimmune dermatosis characterized by well-demarcated erythematous plaques covered with thick, silvery-white lamellar scales.",
        "advice": "Topical corticosteroids combined with calcipotriol (vitamin D analogs), keratolytic agents (salicylic acid), or systemic biologics for extensive disease."
    },
    "seborrheic_dermatitis": {
        "title": "Seborrheic Dermatitis",
        "desc": "Inflammatory scalp disorder linked to Malassezia yeast colonization, presenting as greasy yellowish crusts, scaling, and diffuse erythema.",
        "advice": "Medicated shampoos containing ketoconazole 2%, ciclopirox, or coal tar, coupled with intermittent low-potency topical steroids if inflamed."
    },
    "telogen_effluvium": {
        "title": "Telogen Effluvium",
        "desc": "Diffuse, non-scarring hair shedding caused by premature transition of follicles into the telogen phase, usually 2-3 months following an acute stressor.",
        "advice": "Address underlying triggers (iron/ferritin deficiency, thyroid dysfunction, post-illness stress, nutritional deficits). Hair usually regrows spontaneously."
    },
    "tinea_capitis": {
        "title": "Tinea Capitis",
        "desc": "A fungal dermatophyte infection of scalp hair follicles, presenting as circular scaly patches, broken hair stubble ('black dots'), and lymphadenopathy.",
        "advice": "Systemic antifungal medications (e.g. oral griseofulvin or terbinafine) are necessary; topical therapy alone is insufficient to clear follicular infection."
    },
    "traction_alopecia": {
        "title": "Traction Alopecia",
        "desc": "Hair loss resulting from prolonged, repetitive mechanical tension on hair roots (e.g. tight ponytails, braids, weaves, or heavy extensions).",
        "advice": "Immediately adopt loose, natural hairstyles. Early-stage traction is completely reversible; late-stage scarring requires specialist treatment."
    },
    "trichotillomania": {
        "title": "Trichotillomania",
        "desc": "A compulsive hair-pulling disorder presenting with irregular, bizarre patches of incomplete hair loss with fractured hairs of uneven lengths.",
        "advice": "Multidisciplinary management including behavioral therapy (habit reversal training) and dermatological support."
    },
}

ICD10_CODES = {
    "alopecia_areata": "L63.9 (Alopecia areata, unspecified)",
    "androgenetic_alopecia": "L64.9 (Androgenetic alopecia, unspecified)",
    "contact_dermatitis": "L23.9 (Allergic contact dermatitis, unspecified cause)",
    "dandruff": "L21.0 (Seborrhea capitis / Pityriasis capitis)",
    "folliculitis": "L73.9 (Follicular disorder, unspecified)",
    "folliculitis_decalvans": "L66.2 (Folliculitis decalvans)",
    "lichen_planopilaris": "L66.1 (Lichen planopilaris)",
    "normal_healthy_scalp": "Z00.00 (General medical examination without abnormal findings)",
    "pediculosis_capitis": "B85.0 (Pediculosis due to Pediculus humanus capitis)",
    "psoriasis": "L40.0 (Psoriasis vulgaris / Scalp psoriasis)",
    "seborrheic_dermatitis": "L21.0 (Seborrheic dermatitis of scalp)",
    "telogen_effluvium": "L65.0 (Telogen effluvium)",
    "tinea_capitis": "B35.0 (Tinea barbae and tinea capitis)",
    "traction_alopecia": "L65.8 (Other specified nonscarring hair loss)",
    "trichotillomania": "F63.3 (Trichotillomania / Hair-pulling disorder)",
}


def generate_clinical_pdf(scan_record, patient_name=None, lang="en"):
    """
    Builds a professional 2-page clinical PDF report and doctor referral dossier for a given ScanRecord.
    Returns bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=32,
        leftMargin=32,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    primary_color = colors.HexColor("#1e3a8a")    # Deep Navy
    secondary_color = colors.HexColor("#0f766e")  # Clinical Teal
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    border_color = colors.HexColor("#cbd5e1")
    accent_bg = colors.HexColor("#f8fafc")
    slip_bg = colors.HexColor("#f0fdf4")
    slip_border = colors.HexColor("#16a34a")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=primary_color,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=text_muted,
        spaceAfter=8,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark,
    )
    bold_style = ParagraphStyle(
        "ReportBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9.5,
        textColor=text_muted,
    )

    elements = []

    # =========================================================================
    # PAGE 1: CLINICAL SCREENING, GRAD-CAM & TRICHOMETRIC MORPHOMETRY
    # =========================================================================

    # Header Banner
    header_data = [
        [
            Paragraph("<b>SCALP & HAIR AI CLINICAL SCREENING REPORT</b>", title_style),
            Paragraph(
                f"<b>Report ID:</b> #{scan_record.id:06d}<br/><b>Date:</b> {scan_record.created_at.strftime('%Y-%m-%d %H:%M')}",
                ParagraphStyle("Meta", parent=body_style, alignment=2)
            )
        ]
    ]
    header_table = Table(header_data, colWidths=[370, 178])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Paragraph("Automated Dermatological Analysis & Differential Screening Assessment", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Patient & System Metadata Table
    patient_display = patient_name or (scan_record.user.username if scan_record.user else "Anonymous / Guest Screening")
    status_label = "Review Advised (Low Confidence)" if scan_record.is_uncertain else "Normal Screening Complete"
    meta_info = [
        [
            Paragraph(f"<b>Patient / User:</b> {patient_display}", body_style),
            Paragraph(f"<b>Model Backbone:</b> EfficientNet-B0 (Compound Scaling & Grad-CAM)", body_style),
        ],
        [
            Paragraph(f"<b>Screening Spectrum:</b> 15-Class Scalp Spectrum (84.8% Scaled Cohort Benchmark)", body_style),
            Paragraph(f"<b>Inference Status:</b> {status_label}", body_style),
        ]
    ]
    meta_table = Table(meta_info, colWidths=[274, 274])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Condition Details & Morphological Visuals
    cond_data = CONDITION_INFO.get(scan_record.predicted_label, {
        "title": scan_record.predicted_label.replace("_", " ").title(),
        "desc": "A condition affecting scalp tissue or hair follicle structures.",
        "advice": "Consult a certified medical dermatologist for clinical examination."
    })

    # Prepare Clinical Photo
    image_element = None
    if scan_record.image and os.path.exists(scan_record.image.path):
        try:
            with Image.open(scan_record.image.path) as p_img:
                p_img.load()
            image_element = RLImage(scan_record.image.path, width=105, height=105)
        except Exception:
            image_element = Paragraph("[Image Unavailable]", body_style)
    else:
        image_element = Paragraph("[Image Unavailable]", body_style)

    # Prepare Grad-CAM Heatmap
    gradcam_element = None
    if scan_record.gradcam_base64:
        try:
            raw_bytes = base64.b64decode(scan_record.gradcam_base64)
            with Image.open(io.BytesIO(raw_bytes)) as p_img:
                p_img.load()
            gradcam_element = RLImage(io.BytesIO(raw_bytes), width=105, height=105)
        except Exception as e:
            print("GradCAM decode note:", e)

    if not gradcam_element and scan_record.image and os.path.exists(scan_record.image.path):
        try:
            from .ml_model import _load, _compute_gradcam
            model, grad_model, class_names = _load()
            if grad_model and scan_record.predicted_label in class_names:
                top_idx = class_names.index(scan_record.predicted_label)
                pil_img = Image.open(scan_record.image.path)
                b64_str = _compute_gradcam(pil_img, model, grad_model, top_idx)
                if b64_str:
                    raw_bytes = base64.b64decode(b64_str)
                    gradcam_element = RLImage(io.BytesIO(raw_bytes), width=105, height=105)
        except Exception as e:
            print("Grad-CAM generation note:", e)

    conf_color = "#10b981" if scan_record.confidence >= 75 else ("#f59e0b" if scan_record.confidence >= 50 else "#ef4444")

    from .ml_model import CLINICAL_URGENCY
    urgency = CLINICAL_URGENCY.get(scan_record.predicted_label, {})
    urgency_tier = urgency.get("tier", "ROUTINE")
    urgency_badge = urgency.get("badge", "Clinical Consultation")
    urgency_color = urgency.get("color", "#2563eb")

    status_str = "⚠️ Inconclusive (< 50%)" if scan_record.is_uncertain else "✓ Conclusive Pattern"

    finding_html = f"""
    <b>PRIMARY PREDICTED CONDITION:</b><br/>
    <font size="12" color="#1e3a8a"><b>{cond_data['title']}</b></font><br/><br/>
    <b>AI Confidence:</b> <font color="{conf_color}"><b>{scan_record.confidence:.2f}%</b></font><br/>
    <b>Clinical Triage:</b> <font color="{urgency_color}"><b>[{urgency_tier}] {urgency_badge}</b></font><br/>
    <b>Status:</b> {status_str}<br/><br/>
    <b>Clinical Description:</b><br/>
    {cond_data['desc']}
    """
    finding_para = Paragraph(finding_html, body_style)

    if gradcam_element:
        col_img1 = [Paragraph("<b>Clinical Photo:</b>", body_style), Spacer(1, 2), image_element]
        col_img2 = [Paragraph("<b>Grad-CAM Heatmap:</b>", body_style), Spacer(1, 2), gradcam_element]
        overview_table = Table([[col_img1, col_img2, finding_para]], colWidths=[112, 112, 324])
    else:
        col_img1 = [Paragraph("<b>Clinical Photo:</b>", body_style), Spacer(1, 2), image_element]
        overview_table = Table([[col_img1, finding_para]], colWidths=[140, 408])

    overview_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 8))

    # Trichometry Morphometric Analysis
    tricho = scan_record.trichometry_metrics or {}
    if not tricho and scan_record.image and os.path.exists(scan_record.image.path):
        try:
            from .trichometry_engine import analyze_scalp_metrics
            with Image.open(scan_record.image.path) as p_img:
                tricho = analyze_scalp_metrics(p_img)
        except Exception as e:
            print("PDF Trichometry metrics note:", e)

    if tricho:
        elements.append(Paragraph("Quantitative Scalp Trichometry (Morphometric Analysis)", section_heading))
        h_score = tricho.get("health_score", 0.0)
        h_stage = tricho.get("severity_stage", "Evaluated")
        h_col = tricho.get("stage_color", "#10b981")
        fl_pct = tricho.get("flakiness_pct", 0.0)
        fl_badge = tricho.get("flakiness_badge", "")
        fl_col = tricho.get("flake_color", "#10b981")
        er_pct = tricho.get("erythema_pct", 0.0)
        er_badge = tricho.get("erythema_badge", "")
        er_col = tricho.get("erythema_color", "#10b981")
        exp_pct = tricho.get("scalp_exposure_pct", 0.0)

        tricho_data = [
            [
                Paragraph("<b>Scalp Health Score:</b>", body_style),
                Paragraph(f"<font color='{h_col}'><b>{h_score}/100</b> ({h_stage})</font>", body_style),
                Paragraph("<b>Flakiness & White Scale:</b>", body_style),
                Paragraph(f"<font color='{fl_col}'><b>{fl_pct}%</b> ({fl_badge})</font>", body_style),
            ],
            [
                Paragraph("<b>Scalp Erythema (Redness):</b>", body_style),
                Paragraph(f"<font color='{er_col}'><b>{er_pct}%</b> ({er_badge})</font>", body_style),
                Paragraph("<b>Exposed Scalp Area:</b>", body_style),
                Paragraph(f"<b>{exp_pct}%</b> (Hairline / Parting)", body_style),
            ]
        ]
        tricho_table = Table(tricho_data, colWidths=[120, 154, 120, 154])
        tricho_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), accent_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(tricho_table)
        elements.append(Spacer(1, 8))

    # Differential Diagnosis Breakdown Table
    elements.append(Paragraph("Differential Diagnosis Breakdown (Ranked by Likelihood)", section_heading))
    scores = scan_record.all_scores or {}
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    diff_table_data = [["Rank", "Condition Name", "Probability Score", "Differential Indicator"]]
    for idx, (cls_name, score) in enumerate(sorted_scores[:6], start=1):
        friendly = CONDITION_INFO.get(cls_name, {}).get("title", cls_name.replace("_", " ").title())
        indicator = "Primary Match" if idx == 1 else ("Significant Probability" if score > 10.0 else "Low / Baseline")
        diff_table_data.append([
            f"#{idx}",
            friendly,
            f"{score:.2f}%",
            indicator
        ])

    diff_table = Table(diff_table_data, colWidths=[45, 243, 110, 150])
    diff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, accent_bg]),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
    ]))
    elements.append(diff_table)

    # Page 1 Footer Note
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "<font size='7.5' color='#64748b'>ScalpAI Clinical Diagnostic System • Page 1 of 2 • Official Screening Assessment</font>",
        ParagraphStyle("P1Foot", parent=body_style, alignment=1)
    ))

    # =========================================================================
    # PAGE BREAK -> PAGE 2: THERAPEUTIC REGIMEN & TRIAGE REFERRAL SLIP
    # =========================================================================
    elements.append(PageBreak())

    # Page 2 Header Banner
    p2_header_data = [
        [
            Paragraph("<b>TARGETED THERAPEUTIC REGIMEN & CLINICAL DOSSIER</b>", title_style),
            Paragraph(
                f"<b>Report ID:</b> #{scan_record.id:06d}<br/><b>Status:</b> Official Dossier",
                ParagraphStyle("P2Meta", parent=body_style, alignment=2)
            )
        ]
    ]
    p2_header_table = Table(p2_header_data, colWidths=[370, 178])
    p2_header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(p2_header_table)
    elements.append(Paragraph("Evidence-Based Active Ingredients & Dermatologist Referral Handover", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=8))

    # Treatment Regimen Section
    from .trichometry_engine import get_treatment_recommendation
    tx = scan_record.treatment_summary or get_treatment_recommendation(scan_record.predicted_label)

    elements.append(Paragraph("Recommended Active Ingredient Formulations", section_heading))
    ingredients = tx.get("ingredients", [])
    if ingredients:
        reg_rows = [["Active Compound", "Pharmacological Role & Mechanism"]]
        for ing in ingredients[:3]:
            reg_rows.append([
                Paragraph(f"<b>{ing.get('name', '')}</b>", bold_style),
                Paragraph(ing.get("role", ""), body_style)
            ])
        reg_table = Table(reg_rows, colWidths=[180, 368])
        reg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, accent_bg]),
            ("GRID", (0, 0), (-1, -1), 0.5, border_color),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
        ]))
        elements.append(reg_table)
        elements.append(Spacer(1, 6))

    wash_text = tx.get("wash_routine", "Maintain regular scalp cleansing with dermatological care.")
    avoid_text = tx.get("avoid", "Avoid harsh bleaches, excessive traction tension, and heat treatments.")
    care_box_data = [
        [
            Paragraph(f"<b>Recommended Wash Protocol:</b> {wash_text}<br/><br/><b>Precautions & Ingredients to Avoid:</b> {avoid_text}", body_style)
        ]
    ]
    care_box = Table(care_box_data, colWidths=[548])
    care_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#86efac")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(care_box)
    elements.append(Spacer(1, 10))

    # Clinician Triage Referral Handover Slip (Voucher / Doctor Referral Box)
    hash_seed = f"ScalpAI-{scan_record.id}-{scan_record.created_at.isoformat()}-{scan_record.predicted_label}"
    ref_code = f"REF-{scan_record.id:05d}-" + hashlib.sha256(hash_seed.encode()).hexdigest()[:6].upper()
    icd10_val = ICD10_CODES.get(scan_record.predicted_label, "L65.9 (Unspecified nonscarring hair loss)")

    referral_slip_data = [
        [
            Paragraph("<b>CLINICIAN TRIAGE REFERRAL HANDOVER SLIP</b>", ParagraphStyle("RefTitle", parent=title_style, fontSize=12, leading=15, textColor=primary_color)),
            Paragraph(f"<b>Referral Verification Code:</b> <font color='#16a34a'><b>{ref_code}</b></font>", ParagraphStyle("RefCode", parent=body_style, alignment=2))
        ],
        [
            Paragraph(f"<b>Patient Name:</b> {patient_display}<br/><b>Referring Engine:</b> ScalpAI Clinical Diagnostic System v2.4 Enterprise", body_style),
            Paragraph(f"<b>Triage Priority:</b> <font color='{urgency_color}'><b>[{urgency_tier}] {urgency_badge}</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>Presumptive Primary Finding:</b> {cond_data['title']}<br/><b>Indication ICD-10 Code:</b> {icd10_val}", body_style),
            Paragraph(f"<b>Confidence:</b> {scan_record.confidence:.2f}% (Calibrated Softmax)", body_style)
        ],
        [
            Paragraph(
                "<b>Clinician Physical Review Checklist:</b><br/>"
                "[  ] Primary Diagnosis Verified & Confirmed&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                "[  ] Trichoscopy / Dermatoscopy Completed&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                "[  ] Pharmacological Regimen Prescribed",
                body_style
            ),
            Paragraph("", body_style)
        ],
        [
            Paragraph(
                "<br/><b>Attending Dermatologist / Trichologist Signature & Clinical Stamp:</b><br/>"
                "_____________________________________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: ________________",
                body_style
            ),
            Paragraph(
                "<br/><font size='7' color='#94a3b8'>[ Clinical Stamp / Clinic Seal Box ]</font>",
                ParagraphStyle("Stamp", parent=body_style, alignment=1)
            )
        ]
    ]

    referral_slip = Table(referral_slip_data, colWidths=[360, 188])
    referral_slip.setStyle(TableStyle([
        ("SPAN", (0, 3), (1, 3)),
        ("BACKGROUND", (0, 0), (-1, -1), slip_bg),
        ("BOX", (0, 0), (-1, -1), 1.2, slip_border),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, slip_border),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(referral_slip)
    elements.append(Spacer(1, 10))

    # Medical & Legal Disclaimer Footer
    disclaimer_text = (
        "<b>LEGAL & MEDICAL SCREENING DISCLAIMER:</b> This report is generated by a computer vision deep learning model "
        "(EfficientNet-B0 Compound Scaling with Grad-CAM Visual Heatmaps) trained for educational and preliminary screening assistance only. "
        "This analysis does NOT constitute medical advice, diagnosis, or clinical evaluation. Image quality, lighting, and camera angle "
        "significantly affect model confidence. Always consult a qualified dermatologist or medical practitioner for any scalp or hair health concerns."
    )
    elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "<font size='7.5' color='#64748b'>ScalpAI Clinical Diagnostic System • Page 2 of 2 • Doctor Handover Triage Slip</font>",
        ParagraphStyle("P2Foot", parent=body_style, alignment=1)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
