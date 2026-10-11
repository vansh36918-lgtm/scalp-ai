# Phase 12: Real-time Recovery Comparison Engine (Before & After Diff Inspector) Execution Plan

**Status**: Ready to Execute  
**Target DoD**: Implement an interactive Before & After recovery comparison tool (`/compare/?a=<id>&b=<id>`) and REST API (`GET /api/v1/compare/?a=<id>&b=<id>`) that computes objective morphometric deltas (ΔHealth Score, ΔErythema, ΔFlakiness), renders side-by-side visual image and Grad-CAM comparison, issues an automated clinical progress verdict, and integrates seamless scan selection checkboxes in the dashboard, verified with automated test suites.  
**Dependencies**: `detector/views.py`, `detector/urls.py`, `detector/templates/detector/compare.html`, `detector/templates/detector/dashboard.html`, `detector/tests.py`.

---

## Wave 1: Backend Comparison Engine & REST API Endpoint

### Task 1.1: Delta Calculation & Clinical Verdict Engine
- **Target Files**:
  - `detector/views.py`
  - `detector/urls.py`
- **Description**: Implement `compare_scans_view(request)` and `api_compare_scans_view(request)`:
  - Validates `a` and `b` scan IDs and enforces user authorization.
  - Automatically identifies baseline (older scan) and follow-up (newer scan), computing elapsed days.
  - Computes exact numeric deltas:
    - `delta_health_score` = score_b - score_a
    - `delta_erythema_pct` = erythema_b - erythema_a
    - `relative_erythema_reduction` = ((erythema_a - erythema_b) / erythema_a) * 100
    - `delta_flakiness_pct` = flakiness_b - flakiness_a
    - `relative_flakiness_reduction` = ((flakiness_a - flakiness_b) / flakiness_a) * 100
    - `delta_scalp_exposure_pct` = exposure_b - exposure_a
  - Synthesizes automated clinical verdict:
    - "SIGNIFICANT_IMPROVEMENT"
    - "MODERATE_IMPROVEMENT"
    - "STABLE_MAINTENANCE"
    - "ACTIVE_FLARE_UP"
  - Exposes REST API endpoint `GET /api/v1/compare/?a=<id>&b=<id>`.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.RecoveryComparisonEngineTest`
- **Commit Message**: `feat(compare): implement backend delta calculation and clinical progress verdict engine`

---

## Wave 2: Interactive Before & After Frontend UI & Dashboard Integration

### Task 2.1: Before & After Recovery Comparison Template
- **Target Files**:
  - `detector/templates/detector/compare.html`
- **Description**: Build interactive recovery comparison view:
  - Header showing patient name, elapsed days, and baseline vs. follow-up dates.
  - Side-by-side image comparison cards with tab toggle between Clinical Photos and Grad-CAM Saliency Heatmaps.
  - Color-coded Delta Metric Scorecards with arrows (green `↓` for reduced redness/scaling, green `↑` for increased health score).
  - Prominent Clinical Recovery Verdict banner with actionable care advice.
  - Quick action links back to scan detail or dashboard.

### Task 2.2: Dashboard Scan Selection & Compare Shortcut
- **Target Files**:
  - `detector/templates/detector/dashboard.html`
- **Description**: Add multi-scan comparison capabilities in the dashboard:
  - Add comparison selection checkboxes in the scan history list.
  - Sticky/floating action bar when 2 scans are selected: "Compare 2 Scans (Before & After)".
  - "Compare with Previous" quick shortcut button on historical scan items.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.RecoveryComparisonEngineTest`
- **Commit Message**: `feat(ui): add interactive before & after recovery comparison view and dashboard selector`

---

## Wave 3: Automated Verification, Cloud Deployment & State Synchronization

### Task 3.1: Test Suite Verification & Production Synchronization
- **Target Files**:
  - `detector/tests.py`
  - `.planning/STATE.md`
  - `.planning/ROADMAP.md`
- **Description**: Run full test suite, stage and push git commits to `origin main`, rebuild Docker container on AWS EC2, and verify live endpoints.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector`
- **Commit Message**: `feat(deploy): deploy Phase 12 recovery comparison engine to AWS EC2 production`
