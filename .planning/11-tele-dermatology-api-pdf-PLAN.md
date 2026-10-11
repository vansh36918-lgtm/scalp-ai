# Phase 11: Tele-Dermatology Referral API & Multi-Language Clinical Reports Execution Plan

**Status**: Ready  
**Target DoD**: Implement a production REST API endpoint (`/api/v1/analyze/`) for tele-dermatology clinic integration, upgrade the clinical consultation PDF generator with multi-language localization (English, Spanish, Hindi), longitudinal recovery progress charts, Grad-CAM overlays, and doctor referral triage slips, verified via automated test suites.  
**Dependencies**: `detector/pdf_generator.py`, `detector/views.py`, `detector/urls.py`, `detector/tests.py`, `reportlab`.

---

## Wave 1: Tele-Dermatology Clinic REST API

### Task 1.1: Clinical Analysis & Triage REST API Endpoint
- **Target Files**:
  - `detector/views.py`
  - `detector/urls.py`
- **Description**: Implement `POST /api/v1/analyze/`:
  - Accepts image file upload, validates format and scalp domain guard.
  - Runs full inference pipeline with TTA, trichometry metrics, urgency triage, Grad-CAM overlay, and active ingredient recommendations.
  - Returns structured JSON payload with diagnostic label, calibrated confidence, top-3 differential diagnosis, urgency tier, trichometry indices, and treatment regimen.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.TeleDermatologyApiTest`
- **Commit Message**: `feat(api): implement tele-dermatology analysis and triage REST API endpoint`

---

## Wave 2: Enhanced Multi-Language Clinical PDF Dossier

### Task 2.1: Multi-Language Clinical Consultation Dossier (English, Spanish, Hindi)
- **Target Files**:
  - `detector/pdf_generator.py`
  - `detector/views.py`
- **Description**: Upgrade `generate_clinical_pdf` to support `lang` parameter (`en`, `es`, `hi`):
  - Localized condition titles, descriptions, urgency badges, clinical advice, and active ingredient tables.
  - Formats multi-page clinical consultation dossier:
    - Page 1: Diagnostic overview, Grad-CAM attention heatmap, objective trichometry indices.
    - Page 2: Evidence-based active ingredient regimen, patient recovery instructions, and Clinician Triage Referral Handover slip with scan verification code.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.ClinicalPdfGeneratorTest`
- **Commit Message**: `feat(pdf): add multi-language tele-dermatology consultation dossier and doctor referral slip`

---

## Wave 3: Integration, Test Verification & Cloud Deployment

### Task 3.1: Comprehensive Test Suite & Cloud Production Synchronization
- **Target Files**:
  - `detector/tests.py`
  - `.planning/STATE.md`
  - `.planning/ROADMAP.md`
- **Description**: Run full automated test suite to ensure all tests pass, update documentation, push commits to GitHub `main`, and re-deploy updated container on AWS EC2.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector`
- **Commit Message**: `feat(deploy): synchronize Phase 11 tele-dermatology API and localized reports to AWS EC2`
