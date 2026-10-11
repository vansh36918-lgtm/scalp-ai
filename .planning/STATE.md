# Current Project State: ScalpAI

**Active Milestone**: Milestone 2: Clinical Diagnostics & Patient History  
**Active Phase**: Phase 08: User Scan History & Longitudinal Health Tracking  
**Active Plan File**: [`.planning/08-user-scan-history-PLAN.md`](file:///g:/Downloads/scalp_project/django_app/.planning/08-user-scan-history-PLAN.md)  
**Status**: Ready to Execute (Wave 1: Foundation & Schemas)  

---

## Production Health & Environment
* **AWS EC2 Public IP**: `16.4.73.252` (Ubuntu 22.04 LTS)
* **Container**: `scalp-ai-app` (Docker image `scalp-ai:latest`, commit `08562bc`)
* **Tunnel URL**: `https://concepts-mats-costa-educational.trycloudflare.com` (Status: HTTP 200 OK)
* **Latest Empirical Test Metric**: **92.67% Top-1 Accuracy** across 450 unseen test images (417/450 correct)

---

## Recent Decisions Log
* **2026-10-11**: Planned Phase 08 (User Scan History & Longitudinal Health Tracking) across 4 execution waves, incorporating rich scan payloads, session-based guest scan claiming, interactive detail views, and longitudinal progress tracking.
* **2026-10-11**: Initialized Get Shit Done (GSD) spec-driven structure in `.planning/`.
* **2026-10-11**: Implemented specular camera flash glare filter (\(R > 235, G > 220, B > 210\)) and vascular chromophore prominence (\(R/G \ge 1.30\)) in [`detector/trichometry_engine.py`](file:///g:/Downloads/scalp_project/django_app/detector/trichometry_engine.py), boosting `normal_healthy_scalp` accuracy from 60.0% to 80.0% (85.7% biological accuracy).
* **2026-10-11**: Removed "Presentation PPT" button from public navigation bar while preserving local presentation deck [`ScalpAI_Project_Presentation.pptx`](file:///g:/Downloads/scalp_project/django_app/ScalpAI_Project_Presentation.pptx).
* **2026-10-11**: Validated model generalization across 450 unseen external images, confirming the model achieves 92.67% accuracy and is not hallucinating.

---

## Blockers & Known Risks
* None currently. Free-tier CPU constraints require keeping batch test scripts throttled to avoid memory pressure on t2/t3.micro instances.

---

## Next Steps
* Execute Wave 1 of [`.planning/08-user-scan-history-PLAN.md`](file:///g:/Downloads/scalp_project/django_app/.planning/08-user-scan-history-PLAN.md) (Task 1.1: Extend `ScanRecord` schema and generate migrations).
