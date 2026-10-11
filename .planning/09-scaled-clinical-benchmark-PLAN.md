# Phase 09: Scaled Clinical Cohort Benchmark (150 images/class = 2,250 total) Execution Plan

**Status**: Ready  
**Target DoD**: Automated curation and validation of 150 unique, unseen clinical test images per class across all 15 conditions (2,250 images total in `dataset/scaled_clinical_benchmark/`), followed by high-throughput batch evaluation with Test-Time Augmentation (TTA), computation of the complete $15 \times 15$ confusion matrix, per-class sensitivity/specificity, and an empirical validation report.  
**Dependencies**: `tensorflow`, `detector/ml_model.py`, `detector/trichometry_engine.py`, `Pillow`, `numpy`.

---

## Wave 1: Cohort Architecture & Acquisition Pipeline

### Task 1.1: Scaled Clinical Cohort Curator & Validator
- **Target Files**:
  - `scripts/curate_scaled_cohort.py`
- **Description**: Build an automated clinical dataset assembler that constructs a dedicated unseen cohort of 150 images per class across all 15 clinical classes (total: 2,250 images) into `../dataset/scaled_clinical_benchmark/`.
  - Validate image format (JPG/PNG/WEBP), minimum resolution ($224 \times 224$), color channels (RGB), and md5 deduplication against training set images to ensure 0% data leakage.
- **Verification Command**:
  `..\venv\Scripts\python scripts/curate_scaled_cohort.py --check-only`
- **Commit Message**: `feat(benchmark): create scalable clinical image cohort curation pipeline`

### Task 1.2: Clinical Domain Guard Pre-Filtering
- **Target Files**:
  - `scripts/curate_scaled_cohort.py`
- **Description**: Integrate `verify_scalp_domain()` from `detector/ml_model.py` into the cohort curation pipeline to ensure each gathered image passes biological tissue density, skin hue distribution, and color validity before being accepted into the 2,250 benchmark set.
- **Verification Command**:
  `..\venv\Scripts\python scripts/curate_scaled_cohort.py --verify-domain`
- **Commit Message**: `feat(benchmark): integrate multi-stage domain guard pre-filtering into cohort assembler`

---

## Wave 2: Scaled Batch Evaluation Engine & Metrics

### Task 2.1: High-Throughput Batch Inference Evaluator
- **Target Files**:
  - `scripts/evaluate_scaled_cohort.py`
- **Description**: Build a memory-bounded, batched evaluation engine for the 2,250 images:
  - Supports Test-Time Augmentation (TTA) with batched tensor execution to maximize CPU utilization without exceeding RAM boundaries.
  - Checkpoints progress every 50 images to `scripts/benchmark_checkpoint.json` so execution can be safely resumed or audited.
  - Computes top-1 and top-3 accuracy, calibrated confidence distributions, flakiness, and erythema correlations.
- **Verification Command**:
  `..\venv\Scripts\python scripts/evaluate_scaled_cohort.py --dry-run`
- **Commit Message**: `feat(benchmark): build batched evaluation engine with progress checkpointing`

### Task 2.2: Comprehensive $15 \times 15$ Confusion Matrix & Statistical Analyzer
- **Target Files**:
  - `scripts/evaluate_scaled_cohort.py`
- **Description**: Compute full statistical performance metrics:
  - Exact $15 \times 15$ confusion matrix.
  - Per-class Sensitivity (Recall), Specificity, Positive Predictive Value (Precision), and F1-score.
  - Macro-average and weighted-average accuracy.
  - Quantitative correlation between clinical trichometry indices and model classification confidence.
- **Verification Command**:
  `..\venv\Scripts\python scripts/evaluate_scaled_cohort.py --summary-only`
- **Commit Message**: `feat(benchmark): compute full 15x15 confusion matrix and per-class clinical statistics`

---

## Wave 3: Visualization & Statistical Artifact Reporting

### Task 3.1: Confusion Matrix Heatmap & Report Artifact Generation
- **Target Files**:
  - `scripts/generate_benchmark_charts.py`
  - `C:\Users\ASUS\.gemini\antigravity\brain\c154bd78-de80-4bc0-a973-1cda8a9d23bd\Scaled_Clinical_Cohort_2250_Benchmark_Report.md`
- **Description**: Render a high-resolution confusion matrix heatmap image (`confusion_matrix_scaled_2250.png`) using matplotlib/seaborn, and author the comprehensive statistical report artifact documenting whether the model sustains >90% accuracy across 2,250 unseen test images or reveals any localized sister-class overlap.
- **Verification Command**:
  `..\venv\Scripts\python scripts/generate_benchmark_charts.py`
- **Commit Message**: `feat(benchmark): generate confusion matrix heatmap and comprehensive report artifact`

---

## Wave 4: Integration & Synchronization

### Task 4.1: Full End-to-End Benchmark Execution
- **Target Files**: None (Execution run)
- **Description**: Execute the complete 2,250-image benchmark run across all 15 classes, verify that all 2,250 images are evaluated, check the final accuracy output, and verify zero crashes or memory spikes.
- **Verification Command**:
  `..\venv\Scripts\python scripts/evaluate_scaled_cohort.py`
- **Commit Message**: `chore(benchmark): complete 2,250-sample empirical clinical cohort evaluation`

### Task 4.2: Roadmap & Living State Synchronization
- **Target Files**:
  - `.planning/STATE.md`
  - `.planning/ROADMAP.md`
- **Description**: Synchronize living state, record final multi-class metrics in `STATE.md`, mark Phase 09 complete in `ROADMAP.md`, and push all changes to GitHub `main`.
- **Verification Command**:
  `git status -s`
- **Commit Message**: `docs(gsd): update roadmap and state with Phase 09 scaled benchmark findings`
