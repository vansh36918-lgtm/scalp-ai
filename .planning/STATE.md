# Current Project State: ScalpAI

**Active Milestone**: Milestone 2: Model Hardening & Clinical Generalization  
**Active Phase**: Phase 08: Scaled Clinical Cohort Benchmark (150 images/class)  
**Status**: Ready to plan / Stable in Production  

---

## Production Health & Environment
* **AWS EC2 Public IP**: `16.4.73.252` (Ubuntu 22.04 LTS)
* **Container**: `scalp-ai-app` (Docker image `scalp-ai:latest`, commit `08562bc`)
* **Tunnel URL**: `https://concepts-mats-costa-educational.trycloudflare.com` (Status: HTTP 200 OK)
* **Latest Empirical Test Metric**: **92.67% Top-1 Accuracy** across 450 unseen test images (417/450 correct)

---

## Recent Decisions Log
* **2026-10-11**: Initialized Get Shit Done (GSD) spec-driven structure in `.planning/`.
* **2026-10-11**: Implemented specular camera flash glare filter (\(R > 235, G > 220, B > 210\)) and vascular chromophore prominence (\(R/G \ge 1.30\)) in [`detector/trichometry_engine.py`](file:///g:/Downloads/scalp_project/django_app/detector/trichometry_engine.py), boosting `normal_healthy_scalp` accuracy from 60.0% to 80.0% (85.7% biological accuracy).
* **2026-10-11**: Removed "Presentation PPT" button from public navigation bar while preserving local presentation deck [`ScalpAI_Project_Presentation.pptx`](file:///g:/Downloads/scalp_project/django_app/ScalpAI_Project_Presentation.pptx).
* **2026-10-11**: Validated model generalization across 450 unseen external images, confirming the model achieves 92.67% accuracy and is not hallucinating.

---

## Blockers & Known Risks
* None currently. Free-tier CPU constraints require keeping batch test scripts throttled to avoid memory pressure on t2/t3.micro instances.

---

## Next Steps
* Run `/gsd-plan` or start Phase 08 planning for the 150-images-per-class (2,250 total) extended validation cohort, or begin Phase 09.
