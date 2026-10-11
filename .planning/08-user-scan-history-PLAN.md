# Phase 08: User Scan History & Longitudinal Health Tracking Execution Plan

**Status**: Ready  
**Target DoD**: Enriched `ScanRecord` model (trichometry metrics, clinical urgency, treatment snapshot, and Grad-CAM image), interactive `/scan/<id>/` view, longitudinal recovery timeline chart in dashboard, condition filtering, scan deletion, and guest session claiming; verified via automated test suite.  
**Dependencies**: Django 5.x ORM, existing `ScanRecord` model, `trichometry_engine.py`, `ml_model.py`.

---

## Wave 1: Foundation & Schemas

### Task 1.1: Extend `ScanRecord` Schema
- **Target Files**:
  - `detector/models.py`
  - `detector/migrations/0002_scanrecord_trichometry_metrics_and_more.py`
- **Description**: Add fields to `ScanRecord` to capture full diagnostic context without re-running inference:
  - `trichometry_metrics` (`models.JSONField(default=dict)`)
  - `urgency_tier` (`models.CharField(max_length=50, blank=True)`)
  - `urgency_badge` (`models.CharField(max_length=100, blank=True)`)
  - `treatment_summary` (`models.JSONField(default=dict)`)
  - `gradcam_base64` (`models.TextField(blank=True, null=True)`)
- **Verification Command**:
  `..\venv\Scripts\python manage.py makemigrations detector && ..\venv\Scripts\python manage.py migrate`
- **Commit Message**: `feat(history): extend ScanRecord schema with trichometry, urgency and gradcam fields`

### Task 1.2: Populate Complete Diagnostic Payload in `upload_view`
- **Target Files**:
  - `detector/views.py`
- **Description**: Update `upload_view` to persist `trichometry`, `urgency`, `treatment`, and `gradcam_base64` into the created `ScanRecord`. Also append `scan_record.id` to `request.session['guest_scan_ids']` if the request is unauthenticated.
- **Verification Command**:
  `..\venv\Scripts\python manage.py check`
- **Commit Message**: `feat(history): persist complete trichometry and treatment payload to ScanRecord`

---

## Wave 2: Core Domain Logic & Account Claiming

### Task 2.1: Guest Scan Session Tracking and Account Claiming
- **Target Files**:
  - `detector/views.py`
- **Description**: Implement helper function `claim_guest_scans(request, user)` in `detector/views.py`. Whenever a user logs in via `login_view` or registers via `register_view`, claim any unowned scan records listed in `request.session.get('guest_scan_ids', [])` and associate them with `user`. Clear session key afterward.
- **Verification Command**:
  `..\venv\Scripts\python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scalp_site.settings'); django.setup(); from detector.views import claim_guest_scans; print('Helper loaded')"`
- **Commit Message**: `feat(history): implement session-based guest scan claiming on login and register`

### Task 2.2: Scan Deletion Endpoint
- **Target Files**:
  - `detector/views.py`
  - `detector/urls.py`
- **Description**: Implement `delete_scan_view(request, scan_id)`. Validate that the request method is `POST`, user is authenticated, and `scan_record.user == request.user`. Delete file from media storage and remove database record. Return confirmation message via `django.contrib.messages` and redirect to dashboard.
- **Verification Command**:
  `..\venv\Scripts\python manage.py check`
- **Commit Message**: `feat(history): add secure scan deletion endpoint with ownership authorization`

---

## Wave 3: Interactive Detail View & UI Dashboard

### Task 3.1: Interactive Historical Scan Detail View
- **Target Files**:
  - `detector/views.py`
  - `detector/urls.py`
  - `detector/templates/detector/scan_detail.html`
- **Description**: Implement `scan_detail_view(request, scan_id)` and template `detector/scan_detail.html`. Display:
  - Original scalp photograph and saved Grad-CAM heatmap.
  - Quantitative trichometry metrics (Flakiness %, Erythema %, Exposure %, Health Score).
  - Clinical urgency badge and severity staging.
  - Top-3 differential diagnosis probability breakdown.
  - Customized active ingredient guidance and wash protocol.
  - Link to download official clinical PDF report.
  - Access control: ensure user owns the scan or scan ID is in current session.
- **Verification Command**:
  `..\venv\Scripts\python manage.py check`
- **Commit Message**: `feat(history): create interactive historical scan detail view and template`

### Task 3.2: Dashboard Longitudinal Recovery Timeline & Filters
- **Target Files**:
  - `detector/templates/detector/dashboard.html`
  - `detector/views.py`
- **Description**: Upgrade `dashboard_view` and `detector/dashboard.html`:
  - **Recovery Timeline**: Render an interactive progress visual (HTML5 Canvas / SVG chart) tracking the patient's Scalp Health Score, Erythema %, and Flakiness % chronologically over time.
  - **Condition Filter & Search**: Client-side / query-param filtering by clinical condition and date range.
  - **Quick Actions**: Add "Review Full Scan" link to `/scan/<id>/` and a modal-protected delete button.
- **Verification Command**:
  `..\venv\Scripts\python manage.py check`
- **Commit Message**: `feat(history): enhance dashboard with recovery progress timeline and condition filters`

---

## Wave 4: Integration & Automated Verification

### Task 4.1: Comprehensive Test Suite for Scan History
- **Target Files**:
  - `detector/tests.py`
- **Description**: Write automated tests using Django TestCase covering:
  1. `ScanRecord` creation with trichometry JSON payload.
  2. Guest scan session recording and automatic claiming upon user login.
  3. Authorization enforcement on `scan_detail_view` and `delete_scan_view`.
  4. Deletion of scan record and media cleanup.
  5. Dashboard context calculations (average health score, count, filtering).
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector`
- **Commit Message**: `test(history): add comprehensive automated tests for scan history workflow`

### Task 4.2: End-to-End Verification & Production Deployment
- **Target Files**: None (deployment)
- **Description**: Verify all tests pass locally, push commit to GitHub `main`, trigger Docker rebuild and migration on AWS EC2 (`16.4.73.252`), and test live endpoints over Cloudflare Tunnel.
- **Verification Command**:
  `curl.exe -s -I https://concepts-mats-costa-educational.trycloudflare.com/ping/`
- **Commit Message**: `chore(release): deploy Phase 08 user scan history to production`
