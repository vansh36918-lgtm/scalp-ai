# Project Roadmap: ScalpAI

## Milestone 1: Core System & Deployment (Completed)
- [x] **Phase 01: 15-Class CNN & Grad-CAM Pipeline** (Risk: Low)
  - Definition of Done: EfficientNet-B0 trained, loaded into Django, and generates Grad-CAM saliency heatmaps with calibrated temperature scaling.
- [x] **Phase 02: Computer Vision Trichometry Engine** (Risk: Medium)
  - Definition of Done: Objective flakiness and erythema quantification implemented with active ingredient recommendations.
- [x] **Phase 03: Scalp & Hair Domain Guard** (Risk: Medium)
  - Definition of Done: Out-of-distribution non-scalp photos (documents, anime, digital art) rejected with 0% confidence.
- [x] **Phase 04: Web Application & UI Staging** (Risk: Low)
  - Definition of Done: Responsive web interface with drag-and-drop, sample images, and PDF download.
- [x] **Phase 05: AWS EC2 Docker Deployment & Cloudflare Tunnel** (Risk: High)
  - Definition of Done: Production container running on AWS EC2 (`16.4.73.252`), served over HTTPS via Cloudflare Tunnel.

---

## Milestone 2: Clinical Diagnostics & Patient History (Active)
- [x] **Phase 06: Specular Flash Glare Masking & Healthy Scalp Calibration** (Risk: Medium)
  - Definition of Done: Camera flash glares masked; `normal_healthy_scalp` accuracy elevated to 80.0% (85.7% biological).
- [x] **Phase 07: Unseen Empirical Test Set Evaluation** (Risk: Low)
  - Definition of Done: 450 unseen test images evaluated across all 15 classes; achieved 92.67% overall unseen accuracy.
- [x] **Phase 08: User Scan History & Longitudinal Health Tracking** (Risk: Medium)
  - Definition of Done: Enriched `ScanRecord` model (trichometry metrics, urgency, Grad-CAM snapshot), interactive `/scan/<id>/` view, longitudinal recovery timeline chart in dashboard, condition filtering, scan deletion, and guest session claiming; verified via automated test suite.

---

## Milestone 3: Advanced Diagnostic Capabilities (Future)
- [ ] **Phase 09: Scaled Clinical Cohort Benchmark (150 images/class = 2,250 total)** (Risk: Medium)
  - Definition of Done: Batch collection from dermatological open databases (ISIC/DermNet) with extended multi-class confusion matrix.
- [ ] **Phase 10: Dermoscopic Hair Shaft Caliber Variance Analysis** (Risk: Medium)
  - Definition of Done: Automated detection of miniaturization and flame hairs to further separate `trichotillomania` from `alopecia_areata`.
- [ ] **Phase 11: Tele-Dermatology Referral API & Multi-Language Reports** (Risk: Low)
  - Definition of Done: REST API endpoint for clinic integration and Spanish/Hindi localization of PDF reports.
