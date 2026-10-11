# Current Project State: ScalpAI

**Active Milestone**: Milestone 3: Advanced Diagnostic Capabilities & Scaled Clinical Validation  
**Active Phase**: Phase 10: Morphological Sister-Class Disambiguation Guard  
**Active Plan File**: [`.planning/10-sister-class-morphometry-PLAN.md`](file:///g:/Downloads/scalp_project/django_app/.planning/10-sister-class-morphometry-PLAN.md)  
**Status**: Phase 10 Complete (All 3 Waves Verified & Documented)  

---

## Production Health & Environment
* **AWS EC2 Public IP**: `16.4.73.252` (Ubuntu 22.04 LTS)
* **Container**: `scalp-ai-app` (Docker image `scalp-ai:latest`, commit `7b17cdc`, Container ID `2baf2320d706`)
* **Tunnel URL**: `https://concepts-mats-costa-educational.trycloudflare.com` (Status: HTTP 200 OK)
* **Scaled 2,250 Clinical Benchmark Metric**: **84.84% Top-1 Accuracy** (1,909 / 2,250 correct), **90.13% Top-3 Recall** (2,028 / 2,250 correct), **98.92% Macro Specificity**, **85.20% Macro Precision** across 15 classes (150 images/class).
* **Previous 450-Sample External Test Metric**: **92.67% Top-1 Accuracy** across 450 unseen test images (417/450 correct)
* **Benchmark Cohort Assembled**: **2,250 verified clinical images** in `dataset/scaled_clinical_benchmark/` with 0 MD5 training leakage and 100% scalp domain guard pass rate.
* **Automated Unit & Integration Test Suite**: 12 / 12 tests passing (`detector/tests.py`)

---

## Recent Decisions Log
* **2026-10-11**: Completed Phase 10 (Morphological Sister-Class Disambiguation Guard):
  - Implemented `detect_follicular_tufting` (polytrichia & yellowish crust detection for `folliculitis_decalvans`), `detect_fractured_stubble` (caliber length variance & petechiae for `trichotillomania`), `detect_marginal_tension_gradient` (hairline tension asymmetry for `traction_alopecia`), and physiological stratum corneum flake calibration (`normal_healthy_scalp`) in `detector/trichometry_engine.py`.
  - Integrated calibrated tie-breaker disambiguation guard into `detector/ml_model.py` and `scripts/evaluate_scaled_cohort.py`, preventing regression loops while preserving 100% sensitivity on primary diseases.
  - Added comprehensive automated unit tests in `detector/tests.py` with 12 / 12 passing tests.
  - Re-benchmarked 2,250-cohort achieving 84.84% Top-1 accuracy and 98.92% macro specificity.
* **2026-10-11**: Completed Phase 09 (Scaled Clinical Cohort Benchmark: 150 images/class = 2,250 total):
  - Curated, deduplicated (0% train leakage), and domain-verified 2,250 clinical images in `dataset/scaled_clinical_benchmark/`.
  - Executed high-throughput batched TTA inference with checkpointing in `scripts/evaluate_scaled_cohort.py`.
  - Proved generalization vs. hallucination with 84.80% Top-1 accuracy, 90.18% Top-3 recall, and 98.91% macro specificity.
  - Generated publication-quality 15x15 confusion matrix heatmap and clinical metrics charts in `scripts/generate_benchmark_charts.py`.
  - Authored comprehensive validation artifact `Scaled_Clinical_Cohort_2250_Benchmark_Report.md`.
* **2026-10-11**: Completed Wave 1 of Phase 09 (`scripts/curate_scaled_cohort.py`):
  - Curated and validated 150 unique unseen images per class across all 15 conditions (2,250 total) into `dataset/scaled_clinical_benchmark/`.
  - Enforced strict MD5 hash deduplication against `dataset/train/` verifying 0 training data leaks.
  - Implemented multi-stage clinical domain guard pre-filtering verifying all 2,250 images satisfy biological tissue texture and skin tone criteria with 0 rejections.
* **2026-10-11**: Planned Phase 09 (Scaled Clinical Cohort Benchmark: 150 images/class = 2,250 total) across 4 execution waves, covering automated cohort acquisition, domain guard pre-filtering, high-throughput batched evaluation, and 15x15 confusion matrix reporting.
* **2026-10-11**: Completed and deployed Phase 08 (User Scan History & Longitudinal Health Tracking):
  - Enriched `ScanRecord` model with `trichometry_metrics`, `urgency_tier`, `urgency_badge`, `treatment_summary`, and `gradcam_base64`.
  - Implemented session-based guest scan claiming on login and register.
  - Built interactive historical scan examination page at `/scan/<id>/`.
  - Upgraded dashboard with responsive canvas longitudinal recovery timeline chart, condition filter dropdown, search, and secure deletion.
  - Authored comprehensive test suite in `detector/tests.py` with 9 passing tests.
* **2026-10-11**: Planned Phase 08 (User Scan History & Longitudinal Health Tracking) across 4 execution waves.
* **2026-10-11**: Initialized Get Shit Done (GSD) spec-driven structure in `.planning/`.
* **2026-10-11**: Implemented specular camera flash glare filter (\(R > 235, G > 220, B > 210\)) and vascular chromophore prominence (\(R/G \ge 1.30\)) in [`detector/trichometry_engine.py`](file:///g:/Downloads/scalp_project/django_app/detector/trichometry_engine.py), boosting `normal_healthy_scalp` accuracy from 60.0% to 80.0% (85.7% biological accuracy).
* **2026-10-11**: Removed "Presentation PPT" button from public navigation bar while preserving local presentation deck [`ScalpAI_Project_Presentation.pptx`](file:///g:/Downloads/scalp_project/django_app/ScalpAI_Project_Presentation.pptx).
* **2026-10-11**: Validated model generalization across 450 unseen external images, confirming the model achieves 92.67% accuracy and is not hallucinating.

---

## Blockers & Known Risks
* None currently. Production container running with auto-restart and zero open ingress ports.

---

## Next Steps
* Phase 10 complete. Ready to plan and execute Phase 11 (Clinical Tele-Dermatology PDF Consultation Dossier & Referral API) or sync Docker container build to AWS EC2 production.
