"""
ml_model.py
Loads the trained 15-class EfficientNet-B0 model once and exposes:
  1. Multi-view Test-Time Augmentation (TTA)
  2. Explainable Grad-CAM Attention Heatmap overlay
  3. Clinical Urgency Triage Staging
"""

import json
import io
import base64
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from django.conf import settings

_model = None
_grad_model = None
_class_names = None

CLINICAL_URGENCY = {
    "folliculitis_decalvans": {
        "tier": "URGENT",
        "badge": "Immediate Dermatologist Referral",
        "color": "#dc2626", # red-600
        "bg": "#fef2f2",
        "border": "#fca5a5",
        "rationale": "High risk of permanent cicatricial (scarring) follicle destruction if antimicrobial and anti-inflammatory therapy is delayed."
    },
    "lichen_planopilaris": {
        "tier": "URGENT",
        "badge": "Immediate Specialist Referral",
        "color": "#dc2626",
        "bg": "#fef2f2",
        "border": "#fca5a5",
        "rationale": "Primary lymphocytic cicatricial alopecia causing irreversible hair root destruction; urgent anti-inflammatory therapy needed."
    },
    "alopecia_areata": {
        "tier": "SPECIALIST",
        "badge": "Dermatology Evaluation Recommended",
        "color": "#d97706", # amber-600
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Autoimmune hair loss requiring specialist clinical assessment for intralesional or topical immunotherapy."
    },
    "tinea_capitis": {
        "tier": "SPECIALIST",
        "badge": "Medical Consultation Required",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Dermatophyte infection requiring prescription systemic (oral) antifungal treatment; topical agents alone are ineffective."
    },
    "pediculosis_capitis": {
        "tier": "SPECIALIST",
        "badge": "Pediculicide Eradication Required",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Active parasitic infestation requiring topical pediculicide treatment and contact tracing."
    },
    "psoriasis": {
        "tier": "SPECIALIST",
        "badge": "Dermatology Consultation Recommended",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Chronic autoimmune dermatosis requiring topical corticosteroids, vitamin D analogs, or systemic biologics."
    },
    "telogen_effluvium": {
        "tier": "SPECIALIST",
        "badge": "Clinical Workup Recommended",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Diffuse shedding often triggered by systemic metabolic, thyroid, or nutritional deficiencies requiring lab work."
    },
    "contact_dermatitis": {
        "tier": "ROUTINE",
        "badge": "Allergen Identification & Primary Care",
        "color": "#2563eb", # blue-600
        "bg": "#eff6ff",
        "border": "#93c5fd",
        "rationale": "Acute inflammatory contact reaction; identify and eliminate contactants (dyes, fragrances) with topical symptomatic relief."
    },
    "dandruff": {
        "tier": "ROUTINE",
        "badge": "Over-The-Counter Hygiene Management",
        "color": "#059669", # green-600
        "bg": "#ecfdf5",
        "border": "#6ee7b7",
        "rationale": "Non-inflammatory flaking manageable with over-the-counter therapeutic shampoos (zinc pyrithione, ketoconazole, selenium sulfide)."
    },
    "seborrheic_dermatitis": {
        "tier": "ROUTINE",
        "badge": "Primary Care / Medicated Shampoo",
        "color": "#2563eb",
        "bg": "#eff6ff",
        "border": "#93c5fd",
        "rationale": "Malassezia-associated flaking and erythema responsive to antifungal shampoos and intermittent mild topical steroids."
    },
    "folliculitis": {
        "tier": "ROUTINE",
        "badge": "Antiseptic Wash / Primary Care",
        "color": "#2563eb",
        "bg": "#eff6ff",
        "border": "#93c5fd",
        "rationale": "Superficial bacterial/fungal follicular pustules usually responsive to antibacterial washes or brief targeted antibiotics."
    },
    "androgenetic_alopecia": {
        "tier": "ROUTINE",
        "badge": "Routine Trichology / Non-Urgent",
        "color": "#059669",
        "bg": "#ecfdf5",
        "border": "#6ee7b7",
        "rationale": "Pattern thinning progressing gradually; manageable with topical minoxidil and oral anti-androgens under routine physician advice."
    },
    "traction_alopecia": {
        "tier": "ROUTINE",
        "badge": "Hairstyle Modification / Non-Urgent",
        "color": "#059669",
        "bg": "#ecfdf5",
        "border": "#6ee7b7",
        "rationale": "Mechanical tension induced; reversible in early stages by immediately eliminating tight braids, weaves, or ponytails."
    },
    "trichotillomania": {
        "tier": "SPECIALIST",
        "badge": "Multidisciplinary Care Recommended",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "rationale": "Hair-pulling impulse condition requiring compassionate behavioral therapy and dermatological hair recovery support."
    },
    "normal_healthy_scalp": {
        "tier": "HEALTHY",
        "badge": "Healthy Physiological Scalp",
        "color": "#059669",
        "bg": "#ecfdf5",
        "border": "#6ee7b7",
        "rationale": "No significant signs of active scalp pathology or abnormal follicular destruction detected. Maintain routine hygiene."
    }
}

def _load():
    global _model, _grad_model, _class_names
    if _model is None:
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        _model = load_model(settings.MODEL_PATH)
        with open(settings.CLASS_NAMES_PATH) as f:
            _class_names = json.load(f)

        # Build Grad-CAM gradient model on top_activation
        try:
            last_conv_layer = _model.get_layer("top_activation")
            _grad_model = tf.keras.models.Model(
                [_model.inputs], [last_conv_layer.output, _model.output]
            )
        except Exception:
            _grad_model = None

    return _model, _grad_model, _class_names

def _compute_gradcam(pil_image, model, grad_model, top_class_idx):
    if grad_model is None:
        return None
    import tensorflow as tf
    from tensorflow.keras.applications.efficientnet import preprocess_input

    img_224 = pil_image.convert("RGB").resize((224, 224))
    img_arr = np.array(img_224).astype("float32")
    img_pre = preprocess_input(np.expand_dims(img_arr, axis=0))

    try:
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_pre)
            loss = predictions[:, top_class_idx]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
        heatmap_np = heatmap.numpy()

        # Resize heatmap to match original image dimensions
        heatmap_pil = Image.fromarray(np.uint8(255 * heatmap_np)).resize(pil_image.size, Image.BILINEAR)
        heatmap_arr = np.array(heatmap_pil) / 255.0

        cmap = plt.colormaps.get_cmap("jet")
        jet_colors = np.uint8(255 * cmap(heatmap_arr)[:, :, :3])

        orig_np = np.array(pil_image.convert("RGB"))
        superimposed = np.uint8(orig_np * 0.60 + jet_colors * 0.40)
        res_pil = Image.fromarray(superimposed)

        buf = io.BytesIO()
        res_pil.save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print("Grad-CAM generation error:", e)
        return None

def predict_image(pil_image, enable_tta=True):
    """
    Predicts scalp condition using 15-class EfficientNet-B0 with Test-Time Augmentation,
    explainable Grad-CAM heatmap, and clinical urgency staging.
    """
    import tensorflow as tf
    from tensorflow.keras.applications.efficientnet import preprocess_input

    model, grad_model, class_names = _load()

    # Preprocess primary image
    orig_224 = pil_image.convert("RGB").resize((224, 224))
    arr_orig = preprocess_input(np.expand_dims(np.array(orig_224).astype("float32"), axis=0))

    if enable_tta:
        # 1. Original
        pred_1 = model.predict(arr_orig, verbose=0)[0]
        
        # 2. Horizontal Flip
        flip_224 = orig_224.transpose(Image.FLIP_LEFT_RIGHT)
        arr_flip = preprocess_input(np.expand_dims(np.array(flip_224).astype("float32"), axis=0))
        pred_2 = model.predict(arr_flip, verbose=0)[0]

        # 3. 92% Center Crop
        w, h = pil_image.size
        cw, ch = int(w * 0.92), int(h * 0.92)
        crop_pil = pil_image.crop(((w-cw)//2, (h-ch)//2, (w+cw)//2, (h+ch)//2)).resize((224, 224))
        arr_crop = preprocess_input(np.expand_dims(np.array(crop_pil).astype("float32"), axis=0))
        pred_3 = model.predict(arr_crop, verbose=0)[0]

        predictions = (pred_1 + pred_2 + pred_3) / 3.0
    else:
        predictions = model.predict(arr_orig, verbose=0)[0]

    from .trichometry_engine import analyze_scalp_metrics, get_treatment_recommendation

    # Objective Computer Vision Trichometry Analysis
    metrics = analyze_scalp_metrics(pil_image)

    # Clinical Safety & Photo Flaw Conflict Guard:
    # 1. Healthy Scalp Lighting Glare vs Psoriasis/Dandruff:
    # Healthy scalp skin under flash or bright lighting naturally reflects pinkish tones (12-25% erythema).
    # Only penalize normal_healthy_scalp if flakiness is high (>= 15%) OR erythema is extremely severe (>= 32%).
    if metrics["flakiness_pct"] >= 15.0 or metrics["erythema_pct"] >= 32.0:
        if "normal_healthy_scalp" in class_names:
            norm_idx = class_names.index("normal_healthy_scalp")
            penalized_mass = predictions[norm_idx] * 0.95
            predictions[norm_idx] = predictions[norm_idx] * 0.05

            if metrics["flakiness_pct"] >= 15.0 and metrics["erythema_pct"] >= 20.0 and "psoriasis" in class_names:
                pso_idx = class_names.index("psoriasis")
                predictions[pso_idx] += penalized_mass * 0.70
                if "seborrheic_dermatitis" in class_names:
                    seb_idx = class_names.index("seborrheic_dermatitis")
                    predictions[seb_idx] += penalized_mass * 0.30
            elif "seborrheic_dermatitis" in class_names:
                seb_idx = class_names.index("seborrheic_dermatitis")
                predictions[seb_idx] += penalized_mass * 0.65
                if "dandruff" in class_names:
                    dan_idx = class_names.index("dandruff")
                    predictions[dan_idx] += penalized_mass * 0.35
            elif "dandruff" in class_names:
                dan_idx = class_names.index("dandruff")
                predictions[dan_idx] += penalized_mass

            predictions = predictions / np.sum(predictions)

    top_index = int(np.argmax(predictions))
    label = class_names[top_index]
    confidence = float(predictions[top_index]) * 100.0

    all_scores = {
        class_names[i]: round(float(predictions[i]) * 100.0, 2)
        for i in range(len(class_names))
    }

    # Generate Grad-CAM Attention Heatmap
    gradcam_base64 = _compute_gradcam(pil_image, model, grad_model, top_index)

    # Fetch Clinical Urgency Info
    urgency = CLINICAL_URGENCY.get(label, {
        "tier": "ROUTINE",
        "badge": "Consult Physician",
        "color": "#2563eb",
        "bg": "#eff6ff",
        "border": "#93c5fd",
        "rationale": "Clinical evaluation by a medical professional is advised."
    })

    treatment = get_treatment_recommendation(label)

    return label, round(confidence, 2), all_scores, gradcam_base64, urgency, metrics, treatment
