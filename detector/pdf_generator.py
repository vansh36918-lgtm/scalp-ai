import io
import os
import base64
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
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

def generate_clinical_pdf(scan_record, patient_name=None):
    """
    Builds a professional clinical PDF report for a given ScanRecord.
    Returns bytes buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1e3a8a")  # Deep Navy
    secondary_color = colors.HexColor("#0f766e")  # Clinical Teal
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    border_color = colors.HexColor("#cbd5e1")
    accent_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=15,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=text_dark,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=text_muted,
    )

    elements = []

    # --- Header Banner ---
    header_data = [
        [
            Paragraph("<b>SCALP & HAIR AI CLINICAL SCREENING REPORT</b>", title_style),
            Paragraph(f"<b>Report ID:</b> #{scan_record.id:06d}<br/><b>Date:</b> {scan_record.created_at.strftime('%Y-%m-%d %H:%M')}", ParagraphStyle("Meta", parent=body_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Paragraph("Automated Dermatological Analysis & Differential Screening Assessment", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=12))

    # --- Patient & Scan Metadata ---
    patient_display = patient_name or (scan_record.user.username if scan_record.user else "Anonymous / Guest Screening")
    meta_info = [
        [
            Paragraph(f"<b>Patient / User:</b> {patient_display}", body_style),
            Paragraph(f"<b>Model Backbone:</b> EfficientNet-B0 (Compound Scaling & Grad-CAM)", body_style),
        ],
        [
            Paragraph(f"<b>Screening Classification:</b> 15-Class Scalp Spectrum (84.5% Screening Accuracy)", body_style),
            Paragraph(f"<b>Inference Status:</b> {'Review Advised (Low Confidence)' if scan_record.is_uncertain else 'Normal Screening Complete'}", body_style),
        ]
    ]
    meta_table = Table(meta_info, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # --- Primary Finding & Image ---
    cond_data = CONDITION_INFO.get(scan_record.predicted_label, {
        "title": scan_record.predicted_label.replace("_", " ").title(),
        "desc": "A condition affecting scalp and hair follicles.",
        "advice": "Consult a certified dermatologist for professional diagnosis."
    })

    # Prepare Image
    image_element = None
    if scan_record.image and os.path.exists(scan_record.image.path):
        try:
            image_element = RLImage(scan_record.image.path, width=115, height=115)
        except Exception:
            image_element = Paragraph("[Image Preview Unavailable]", body_style)
    else:
        image_element = Paragraph("[Image Preview Unavailable]", body_style)

    # Attempt to generate Grad-CAM visualization
    gradcam_element = None
    if scan_record.image and os.path.exists(scan_record.image.path):
        try:
            from .ml_model import _load, _compute_gradcam
            model, grad_model, class_names = _load()
            if grad_model and scan_record.predicted_label in class_names:
                top_idx = class_names.index(scan_record.predicted_label)
                pil_img = Image.open(scan_record.image.path)
                b64_str = _compute_gradcam(pil_img, model, grad_model, top_idx)
                if b64_str:
                    raw_bytes = base64.b64decode(b64_str)
                    gradcam_element = RLImage(io.BytesIO(raw_bytes), width=115, height=115)
        except Exception as e:
            print("Grad-CAM PDF embed exception:", e)

    conf_color = "#10b981" if scan_record.confidence >= 75 else ("#f59e0b" if scan_record.confidence >= 50 else "#ef4444")
    
    # Urgency data
    from .ml_model import CLINICAL_URGENCY
    urgency = CLINICAL_URGENCY.get(scan_record.predicted_label, {})
    urgency_tier = urgency.get("tier", "ROUTINE")
    urgency_badge = urgency.get("badge", "Clinical Consultation")
    urgency_color = urgency.get("color", "#2563eb")
    urgency_rationale = urgency.get("rationale", "")

    finding_html = f"""
    <b>PRIMARY PREDICTED CONDITION:</b><br/>
    <font size="14" color="#1e3a8a"><b>{cond_data['title']}</b></font><br/><br/>
    <b>AI Confidence:</b> <font color="{conf_color}"><b>{scan_record.confidence:.2f}%</b></font><br/>
    <b>Clinical Triage:</b> <font color="{urgency_color}"><b>[{urgency_tier}] {urgency_badge}</b></font><br/>
    <b>Status:</b> {'⚠️ Inconclusive (&lt; 50%)' if scan_record.is_uncertain else '✓ Conclusive Pattern'}<br/><br/>
    <b>Clinical Description:</b><br/>
    {cond_data['desc']}
    """
    finding_para = Paragraph(finding_html, body_style)

    if gradcam_element:
        col_img1 = [Paragraph("<b>Clinical Photo:</b>", body_style), Spacer(1, 3), image_element]
        col_img2 = [Paragraph("<b>Grad-CAM Heatmap:</b>", body_style), Spacer(1, 3), gradcam_element]
        overview_table = Table([[col_img1, col_img2, finding_para]], colWidths=[120, 120, 300])
    else:
        overview_table = Table([[image_element, finding_para]], colWidths=[160, 380])

    overview_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 10))

    # --- Quantitative Scalp Trichometry Table ---
    tricho = None
    tx = None
    try:
        from .trichometry_engine import analyze_scalp_metrics, get_treatment_recommendation
        if scan_record.image and os.path.exists(scan_record.image.path):
            with Image.open(scan_record.image.path) as p_img:
                tricho = analyze_scalp_metrics(p_img)
            tx = get_treatment_recommendation(scan_record.predicted_label)
    except Exception as e:
        print("PDF Trichometry engine exception:", e)

    if tricho:
        elements.append(Paragraph("Quantitative Scalp Trichometry (Morphometric Analysis)", section_heading))
        tricho_data = [
            [
                Paragraph("<b>Scalp Health Score:</b>", body_style),
                Paragraph(f"<font color='{tricho['stage_color']}'><b>{tricho['health_score']}/100</b> ({tricho['severity_stage']})</font>", body_style),
                Paragraph("<b>Flakiness & White Scale:</b>", body_style),
                Paragraph(f"<font color='{tricho['flake_color']}'><b>{tricho['flakiness_pct']}%</b> ({tricho['flakiness_badge']})</font>", body_style),
            ],
            [
                Paragraph("<b>Scalp Erythema (Redness):</b>", body_style),
                Paragraph(f"<font color='{tricho['erythema_color']}'><b>{tricho['erythema_pct']}%</b> ({tricho['erythema_badge']})</font>", body_style),
                Paragraph("<b>Exposed Scalp Area:</b>", body_style),
                Paragraph(f"<b>{tricho['scalp_exposure_pct']}%</b> (Hairline / Parting)", body_style),
            ]
        ]
        tricho_table = Table(tricho_data, colWidths=[120, 150, 120, 150])
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
        elements.append(Spacer(1, 10))

    # --- Differential Diagnosis Table ---
    elements.append(Paragraph("Differential Diagnosis Breakdown (Ranked by Likelihood)", section_heading))
    
    scores = scan_record.all_scores or {}
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    diff_table_data = [["Rank", "Condition Name", "Probability Score", "Differential Indicator"]]
    for idx, (cls_name, score) in enumerate(sorted_scores[:8], start=1):
        friendly_name = CONDITION_INFO.get(cls_name, {}).get("title", cls_name.replace("_", " ").title())
        indicator = "Primary Match" if idx == 1 else ("Significant Probability" if score > 10 else "Low / Baseline")
        diff_table_data.append([
            f"#{idx}",
            friendly_name,
            f"{score:.2f}%",
            indicator
        ])

    diff_table = Table(diff_table_data, colWidths=[40, 240, 110, 150])
    diff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, accent_bg]),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ]))
    elements.append(diff_table)
    elements.append(Spacer(1, 10))

    # --- Clinical Next Steps & Guidance ---
    elements.append(Paragraph("Recommended Clinical Next Steps & Regimen", section_heading))
    tx_text = ""
    if tx:
        ing_items = "<br/>".join([f"&bull; <b>{i['name']}</b>: {i['role']}" for i in tx['ingredients'][:3]])
        tx_text = f"<br/><br/><b>Targeted Medical Regimen:</b><br/>{ing_items}<br/><br/><b>Wash Protocol:</b> {tx['wash_routine']}<br/><br/><b>Precautions & Avoid:</b> {tx['avoid']}"

    guidance_text = f"""
    <b>Triage Recommendation:</b> [{urgency_tier}] {urgency_badge} &mdash; {urgency_rationale}<br/><br/>
    <b>Standard Clinical Guidance:</b> {cond_data['advice']}{tx_text}
    """
    guidance_table = Table([[Paragraph(guidance_text, body_style)]], colWidths=[540])
    guidance_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#86efac")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(guidance_table)
    elements.append(Spacer(1, 12))

    # --- Disclaimer Footer ---
    disclaimer_text = """
    <b>LEGAL & MEDICAL SCREENING DISCLAIMER:</b> This report is generated by a computer vision deep learning model (EfficientNet-B0 Compound Scaling with Grad-CAM Visual Heatmaps) trained for educational and preliminary screening assistance only. This analysis does NOT constitute medical advice, diagnosis, or clinical evaluation. Image quality, lighting, and camera angle significantly affect model confidence. Always consult a qualified dermatologist or medical practitioner for any scalp or hair health concerns.
    """
    elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=6))
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
