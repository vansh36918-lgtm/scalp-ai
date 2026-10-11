# Project: ScalpAI (Clinical Scalp & Hair Pathology Diagnostic Engine)

## 1. Overview
ScalpAI is an intelligent clinical decision-support and computer vision system designed to diagnose scalp and hair conditions from standard smartphone and trichoscopy photos. The platform combines deep convolutional neural networks with algorithmic trichometry to deliver fast, explainable, and calibrated dermatological assessments across 15 clinical classes.

### Primary Problems Solved
1. **Dermatologist Accessibility Gap**: Provides immediate, preliminary clinical triage and active ingredient guidance for underserved or remote patients.
2. **Objective Computer Vision Quantification**: Replaces subjective visual estimation with quantitative flakiness (desquamation) and erythema (inflammation) indices.
3. **Anti-Hallucination & Domain Integrity**: Actively rejects non-biological, document, UI, and wallpaper images, preventing model hallucinations on out-of-distribution inputs.

---

## 2. Architecture & Tech Stack

### Core Technologies
- **Language / Runtime**: Python 3.10
- **Web Framework**: Django 5.x (with WhiteNoise for static asset delivery)
- **Deep Learning Framework**: TensorFlow 2.15 / Keras
- **Neural Backbone**: EfficientNet-B0 (fine-tuned on 15 scalp & hair pathological classes)
- **Explainability**: Grad-CAM (Gradient-weighted Class Activation Mapping) on convolutional feature maps
- **Computer Vision Engine**: Custom NumPy / PIL / OpenCV trichometry pipeline
- **Application Server**: Gunicorn (WSGI) in Docker container
- **Infrastructure & Cloud**: AWS EC2 (t2/t3 Ubuntu), automated systemd daemon, Cloudflare Tunnel for secure HTTPS edge routing

### System Architecture Pipeline
```
[User Image]
     │
     ▼
[Domain Rejection Guard] ──(Non-scalp)──► [Rejection Notice (0% confidence)]
     │ (Valid scalp)
     ▼
[Trichometry Engine] ───────────────────► [Flakiness %, Erythema %, Exposure %]
     │
     ▼
[EfficientNet-B0 with TTA] ─────────────► [Raw Softmax Probabilities]
     │
     ▼
[Conflict Guard & Glare Mask] ──────────► [Calibrated Softmax (T=0.18)]
     │
     ▼
[Grad-CAM + Urgency + Treatments] ──────► [Clinical Report & Top-3 Differential]
```

---

## 3. Core Constraints & Guardrails

1. **Zero Cloud Cost / Free-Tier Optimization**:
   - Must operate stably on AWS EC2 micro instances (< 1GB RAM).
   - CPU-only inference; images downsampled to $\le 600\text{px}$ before feature extraction to guarantee memory usage $< 40\text{MB}$ per request.
2. **Clinical Safety & Sensitivity**:
   - Bias toward disease detection over false reassurance (prevent false negatives on subtle infections or scarring alopecias).
   - Top-3 differential diagnoses always provided to handle clinical spectrum overlaps (e.g. dandruff vs. seborrheic dermatitis).
3. **Privacy & Data Security**:
   - Uploaded diagnostic images are processed in-memory and not persisted to databases or public storage without consent.
