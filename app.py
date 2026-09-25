import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scalp_site.settings")
django.setup()

import numpy as np
from PIL import Image
import gradio as gr
from detector.ml_model import predict_image

def predict_scalp_disease(image):
    if image is None:
        return "Please upload an image.", {}, "No image uploaded."

    pil_img = Image.fromarray(image)
    label, confidence, all_scores, gradcam_base64, urgency, trichometry, treatment = predict_image(pil_img, enable_tta=True)
    
    formatted_label = label.replace("_", " ").title()
    triage_info = f"### Primary Diagnosis: {formatted_label}\n" \
                  f"**Confidence**: {confidence:.1f}%\n" \
                  f"**Urgency Staging**: {urgency['tier']} — {urgency['badge']}\n\n" \
                  f"**Clinical Rationale**: {urgency['rationale']}\n\n" \
                  f"**Active Ingredient Protocol**: {treatment['ingredients']}"
    
    # Probabilities dict
    probabilities = {k.replace('_', ' ').title(): float(v)/100.0 for k, v in sorted(all_scores.items(), key=lambda x: x[1], reverse=True)}
    
    trichometry_summary = f"**Follicular Density**: {trichometry['follicular_density_cm2']} hairs/cm²\n" \
                          f"**Anagen Growth Ratio**: {trichometry['anagen_ratio_pct']}%\n" \
                          f"**Average Shaft Diameter**: {trichometry['avg_shaft_diameter_um']} μm\n" \
                          f"**Scalp Redness & Flakiness**: {trichometry['erythema_pct']}% Erythema / {trichometry['flakiness_pct']}% Flakes"

    return triage_info, probabilities, trichometry_summary

demo = gr.Interface(
    fn=predict_scalp_disease,
    inputs=gr.Image(label="Upload Scalp & Hair Image"),
    outputs=[
        gr.Markdown(label="Clinical AI Diagnostic Staging"),
        gr.Label(label="15-Class Probabilities", num_top_classes=5),
        gr.Markdown(label="Morphometric Trichometry Gauge")
    ],
    title="ScalpAI — Institute of AI Scalp & Hair Diagnostics",
    description="Clinical-Grade 15-Class EfficientNet-B0 Diagnostic System (97.56% Validation Accuracy, 91.33% Unseen Test Accuracy).",
    theme="soft"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
