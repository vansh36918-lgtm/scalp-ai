# Phase 10: Morphological Sister-Class Disambiguation Guard Execution Plan

**Status**: Ready  
**Target DoD**: Implement automated computer-vision morphometric detectors for tufted hair clustering (polytrichia for `folliculitis_decalvans`), fractured stubble caliber variance (`trichotillomania`), marginal hairline tension banding (`traction_alopecia`), and physiological stratum corneum flake calibration (`normal_healthy_scalp`). Integrate these features into `detector/ml_model.py` conflict triage, and re-evaluate the 2,250-sample clinical benchmark cohort to achieve >90% overall clinical accuracy with significant gains on all 4 sister-class conditions.  
**Dependencies**: `detector/trichometry_engine.py`, `detector/ml_model.py`, `detector/tests.py`, `scripts/evaluate_scaled_cohort.py`.

---

## Wave 1: Trichometric Morphometry Feature Extraction

### Task 1.1: Tufted Follicle (Polytrichia) & Scalp Cicatricial Indicator
- **Target Files**:
  - `detector/trichometry_engine.py`
- **Description**: Implement `detect_follicular_tufting(pil_image)` in `detector/trichometry_engine.py`:
  - Analyzes high-contrast dark hair roots emerging from common inflamed ostia.
  - Detects "doll's hair" sign characteristic of folliculitis decalvans (clusters of 5–12 hairs) with yellowish peripilar crusts.
  - Returns `tufting_score` (0.0–1.0) and boolean `tufting_detected`.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.TrichometryEngineTests.test_tufted_follicle_detection`
- **Commit Message**: `feat(trichometry): implement polytrichia tufted follicle detector`

### Task 1.2: Fractured Hair Stubble & Caliber Variance Analyzer
- **Target Files**:
  - `detector/trichometry_engine.py`
- **Description**: Implement `detect_fractured_stubble(pil_image)` in `detector/trichometry_engine.py`:
  - Quantifies morphological hair length standard deviation across detected dark hair segments.
  - Detects blunt fractured hair stubs (5–30px) and mechanical pulling petechial marks characteristic of trichotillomania, distinguishing them from the smooth bald skin of alopecia areata.
  - Returns `stubble_variance_score` (0.0–1.0) and `fractured_stubble_detected`.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.TrichometryEngineTests.test_fractured_stubble_detection`
- **Commit Message**: `feat(trichometry): implement fractured hair stubble and caliber variance analyzer`

### Task 1.3: Marginal Tension Hairline Gradient & Physiological Flake Calibration
- **Target Files**:
  - `detector/trichometry_engine.py`
- **Description**: 
  - Implement `detect_marginal_tension_gradient(pil_image)`: calculates directional density asymmetry along hairline borders to capture the "fringe sign" in traction alopecia.
  - Calibrate physiological stratum corneum vs true dandruff in `analyze_scalp_metrics()`: when erythema < 7% and flakiness is composed of isolated micro-specks without confluent scaling, classify as physiological dry scalp rather than active seborrhea/dandruff.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector.tests.TrichometryEngineTests.test_tension_gradient_and_physiological_flaking`
- **Commit Message**: `feat(trichometry): add marginal tension gradient and calibrate physiological flaking`

---

## Wave 2: Neural Classification Re-Ranking & Conflict Guard Integration

### Task 2.1: Integrated Multi-Modal Sister-Class Disambiguation Guard
- **Target Files**:
  - `detector/ml_model.py`
- **Description**: Integrate the new morphometric indicators into `predict_image()` in `detector/ml_model.py`:
  - If `tufting_detected` is positive and model predicts `lichen_planopilaris` or `folliculitis`, re-weight mass toward `folliculitis_decalvans`.
  - If `fractured_stubble_detected` is positive and model predicts `alopecia_areata`, re-weight mass toward `trichotillomania`.
  - If `marginal_tension_gradient` is strong and model predicts `androgenetic_alopecia` / `alopecia_areata`, re-weight mass toward `traction_alopecia`.
  - If flakiness is < 12%, erythema < 7%, and model predicts `dandruff` over `normal_healthy_scalp`, protect physiological healthy scalp classification.
- **Verification Command**:
  `..\venv\Scripts\python manage.py test detector`
- **Commit Message**: `feat(ml): integrate morphometric sister-class disambiguation guard into clinical prediction`

---

## Wave 3: Cohort Verification & Empirical Re-Benchmarking

### Task 3.1: 2,250 Clinical Benchmark Re-Evaluation & Chart Generation
- **Target Files**:
  - `scripts/evaluate_scaled_cohort.py`
  - `scripts/generate_benchmark_charts.py`
  - `scripts/benchmark_results.json`
  - `scripts/benchmark_summary.json`
- **Description**: Re-run the full 2,250-sample clinical benchmark with the new morphometric disambiguation engine:
  - Measure sensitivity increases across all 4 targeted conditions.
  - Confirm overall Top-1 clinical accuracy exceeds 90% and Top-3 recall exceeds 94%.
  - Regenerate updated confusion matrix heatmap and clinical metrics charts.
- **Verification Command**:
  `..\venv\Scripts\python scripts/evaluate_scaled_cohort.py --no-resume`
- **Commit Message**: `feat(benchmark): re-evaluate 2,250 cohort with morphometric disambiguation guard`

### Task 3.2: Roadmap, State & Artifact Synchronization
- **Target Files**:
  - `.planning/STATE.md`
  - `.planning/ROADMAP.md`
  - `C:\Users\ASUS\.gemini\antigravity\brain\c154bd78-de80-4bc0-a973-1cda8a9d23bd\Scaled_Clinical_Cohort_2250_Benchmark_Report.md`
- **Description**: Update the report artifact with the new improved metrics, mark Phase 10 complete in `ROADMAP.md`, update `STATE.md`, and push all commits to GitHub `main`.
- **Verification Command**:
  `git status -s`
- **Commit Message**: `docs(gsd): mark Phase 10 complete in roadmap and update benchmark report`
