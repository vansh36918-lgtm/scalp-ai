# Current Project State: ScalpAI

**Active Milestone**: Milestone 2: Clinical Diagnostics & Patient History  
**Active Phase**: Phase 08: User Scan History & Longitudinal Health Tracking (Completed)  
**Active Plan File**: [`.planning/08-user-scan-history-PLAN.md`](file:///g:/Downloads/scalp_project/django_app/.planning/08-user-scan-history-PLAN.md)  
**Status**: Complete & Live in Production  

---

## Production Health & Environment
* **AWS EC2 Public IP**: `16.4.73.252` (Ubuntu 22.04 LTS)
* **Container**: `scalp-ai-app` (Docker image `scalp-ai:latest`, commit `7b17cdc`, Container ID `2baf2320d706`)
* **Tunnel URL**: `https://concepts-mats-costa-educational.trycloudflare.com` (Status: HTTP 200 OK)
* **Latest Empirical Test Metric**: **92.67% Top-1 Accuracy** across 450 unseen test images (417/450 correct)
* **Automated Unit & Integration Test Suite**: 9 / 9 tests passing (`detector/tests.py`)

---

## Recent Decisions Log
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
* Plan Phase 09: Scaled Clinical Cohort Benchmark (curating and evaluating 150 images/class = 2,250 total), or Phase 10: Dermoscopic Hair Shaft Caliber Variance Analysis.
