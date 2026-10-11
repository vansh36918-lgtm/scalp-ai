#!/usr/bin/env python3
"""
evaluate_scaled_cohort.py
Phase 09: Scaled Clinical Cohort Benchmark (150 images/class = 2,250 total)

High-throughput, memory-bounded batch evaluation engine:
  - Batched Test-Time Augmentation (TTA: primary, horizontal flip, center crop).
  - Production-grade Trichometry recalibration & temperature calibration (T=0.18).
  - Safe progress checkpointing every 50 images (scripts/benchmark_checkpoint.json).
  - Exact 15x15 Confusion Matrix computation.
  - Per-class clinical metrics: Sensitivity (Recall), Specificity, Precision (PPV), F1-Score.
  - Quantitative trichometry correlation analysis.
"""

import os
import sys
import argparse
import json
import time
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "dataset", "scaled_clinical_benchmark")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "scripts", "benchmark_checkpoint.json")
RESULTS_FILE = os.path.join(BASE_DIR, "scripts", "benchmark_results.json")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["DJANGO_SETTINGS_MODULE"] = "scalp_site.settings"
import django
django.setup()

from detector.ml_model import _load
from detector.trichometry_engine import analyze_scalp_metrics
from tensorflow.keras.applications.efficientnet import preprocess_input

def get_class_list():
    _, _, class_names = _load()
    return class_names

def run_batched_evaluation(max_per_class=None, batch_size=32, resume=True):
    print("=" * 80)
    print("STARTING SCALED CLINICAL BENCHMARK EVALUATION (2,250 UNSEEN IMAGES)")
    print("=" * 80)

    model, _, class_names = _load()
    num_classes = len(class_names)
    class_to_idx = {name: i for i, name in enumerate(class_names)}

    # Discover benchmark samples
    all_samples = []
    for cls in class_names:
        cls_dir = os.path.join(BENCHMARK_DIR, cls)
        if not os.path.exists(cls_dir):
            continue
        files = sorted([f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if max_per_class is not None:
            files = files[:max_per_class]
        for f in files:
            all_samples.append({
                "true_class": cls,
                "filepath": os.path.join(cls_dir, f),
                "filename": f
            })

    total_samples = len(all_samples)
    print(f"Total benchmark images queued for evaluation: {total_samples}")
    if max_per_class:
        print(f"Running in limited mode ({max_per_class} images per class = {total_samples} total).")

    # Load existing checkpoint if resuming
    results = []
    processed_paths = set()
    if resume and os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                checkpoint_data = json.load(f)
                results = checkpoint_data.get("results", [])
                processed_paths = {r["filepath"] for r in results}
                print(f"Resuming from checkpoint: {len(results)} images already evaluated.")
        except Exception as e:
            print(f"[WARN] Could not load checkpoint: {e}")
            results = []

    remaining_samples = [s for s in all_samples if s["filepath"] not in processed_paths]
    print(f"Remaining images to evaluate: {len(remaining_samples)}")

    start_time = time.time()
    last_checkpoint_time = start_time

    # Process in batches
    for b_idx in range(0, len(remaining_samples), batch_size):
        batch_samples = remaining_samples[b_idx: b_idx + batch_size]
        b_len = len(batch_samples)

        # Arrays for 3 TTA views
        arr_orig = np.zeros((b_len, 224, 224, 3), dtype=np.float32)
        arr_flip = np.zeros((b_len, 224, 224, 3), dtype=np.float32)
        arr_crop = np.zeros((b_len, 224, 224, 3), dtype=np.float32)
        batch_metrics = []

        for i, item in enumerate(batch_samples):
            with Image.open(item["filepath"]) as raw_img:
                pil_img = raw_img.convert("RGB")
                if max(pil_img.width, pil_img.height) > 600:
                    pil_img.thumbnail((600, 600), Image.LANCZOS)

                # 1. Primary 224x224
                orig_224 = pil_img.resize((224, 224))
                arr_orig[i] = np.array(orig_224).astype("float32")

                # 2. Horizontal Flip
                flip_224 = orig_224.transpose(Image.FLIP_LEFT_RIGHT)
                arr_flip[i] = np.array(flip_224).astype("float32")

                # 3. Center crop 92%
                w, h = pil_img.size
                cw, ch = int(w * 0.92), int(h * 0.92)
                crop_pil = pil_img.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)).resize((224, 224))
                arr_crop[i] = np.array(crop_pil).astype("float32")

                # Trichometry analysis
                m = analyze_scalp_metrics(pil_img)
                batch_metrics.append(m)

        # Batch preprocessing
        arr_orig = preprocess_input(arr_orig)
        arr_flip = preprocess_input(arr_flip)
        arr_crop = preprocess_input(arr_crop)

        # Batched C++ forward pass
        preds_1 = model(arr_orig, training=False).numpy()
        preds_2 = model(arr_flip, training=False).numpy()
        preds_3 = model(arr_crop, training=False).numpy()
        batch_preds = (preds_1 + preds_2 + preds_3) / 3.0

        for i, item in enumerate(batch_samples):
            predictions = batch_preds[i]
            metrics = batch_metrics[i]

            # Clinical Conflict Guard (identical to ml_model.py production logic)
            if (metrics["flakiness_pct"] >= 20.0 and metrics["erythema_pct"] >= 35.0) or metrics["erythema_pct"] >= 58.0:
                if "normal_healthy_scalp" in class_names:
                    norm_idx = class_names.index("normal_healthy_scalp")
                    penalized_mass = predictions[norm_idx] * 0.95
                    predictions[norm_idx] = predictions[norm_idx] * 0.05

                    if metrics["flakiness_pct"] >= 15.0 and metrics["erythema_pct"] >= 20.0 and "psoriasis" in class_names:
                        pso_idx = class_names.index("psoriasis")
                        predictions[pso_idx] += penalized_mass * 0.70
                        if "seborrheic_dermatitis" in class_names:
                            seb_idx = class_names.index("seborrheic_dermatitis")
                            predictions[seb_idx] += penalized_mass * 0.30
                    elif "seborrheic_dermatitis" in class_names:
                        seb_idx = class_names.index("seborrheic_dermatitis")
                        predictions[seb_idx] += penalized_mass * 0.65
                        if "dandruff" in class_names:
                            dan_idx = class_names.index("dandruff")
                            predictions[dan_idx] += penalized_mass * 0.35
                    elif "dandruff" in class_names:
                        dan_idx = class_names.index("dandruff")
                        predictions[dan_idx] += penalized_mass

                    predictions = predictions / np.sum(predictions)

            # Morphological Sister-Class Disambiguation Guard
            if metrics.get("is_physiological_flaking", False) and "normal_healthy_scalp" in class_names and "dandruff" in class_names:
                dan_idx = class_names.index("dandruff")
                norm_idx = class_names.index("normal_healthy_scalp")
                if predictions[dan_idx] > predictions[norm_idx] and predictions[dan_idx] < 0.55:
                    transfer = predictions[dan_idx] * 0.45
                    predictions[dan_idx] -= transfer
                    predictions[norm_idx] += transfer

            p_sorted = np.sort(predictions)
            if (p_sorted[-1] - p_sorted[-2]) < 0.12 and p_sorted[-1] < 0.40:
                if metrics.get("tufting_detected", False) and "folliculitis_decalvans" in class_names:
                    fd_idx = class_names.index("folliculitis_decalvans")
                    predictions[fd_idx] += 0.10
                if metrics.get("stubble_detected", False) and "trichotillomania" in class_names:
                    tricho_idx = class_names.index("trichotillomania")
                    predictions[tricho_idx] += 0.10
                if metrics.get("tension_detected", False) and "traction_alopecia" in class_names:
                    trac_idx = class_names.index("traction_alopecia")
                    predictions[trac_idx] += 0.10

            predictions = predictions / np.sum(predictions)
            temp = 0.18
            log_preds = np.log(np.clip(predictions, 1e-7, 1.0)) / temp
            calibrated_preds = np.exp(log_preds - np.max(log_preds))
            calibrated_preds = calibrated_preds / np.sum(calibrated_preds)

            top_idx = int(np.argmax(calibrated_preds))
            top_class = class_names[top_idx]
            top3_indices = [int(idx) for idx in np.argsort(calibrated_preds)[-3:][::-1]]
            top3_classes = [class_names[idx] for idx in top3_indices]

            p_top_cal = float(calibrated_preds[top_idx]) * 100.0
            p_top_raw = float(predictions[top_idx])
            p_second_raw = float(np.sort(predictions)[-2])
            if p_top_cal < 78.0 and p_top_raw > (1.0 / num_classes):
                margin = p_top_raw - p_second_raw
                confidence = min(97.5, 78.5 + (p_top_raw * 32.0) + (margin * 40.0))
            else:
                confidence = p_top_cal

            is_top1 = (top_class == item["true_class"])
            is_top3 = (item["true_class"] in top3_classes)

            results.append({
                "filepath": item["filepath"],
                "filename": item["filename"],
                "true_class": item["true_class"],
                "pred_class": top_class,
                "confidence": round(confidence, 2),
                "top3_classes": top3_classes,
                "is_top1_correct": is_top1,
                "is_top3_correct": is_top3,
                "erythema_pct": metrics["erythema_pct"],
                "flakiness_pct": metrics["flakiness_pct"],
                "scalp_exposure_pct": metrics["scalp_exposure_pct"],
                "health_score": metrics["health_score"],
            })

        # Save checkpoint periodically (every 50 images or upon completion)
        if len(results) % 50 == 0 or len(results) == total_samples:
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump({"total_samples": total_samples, "results": results}, f)
            elapsed = time.time() - start_time
            rate = len(results) / max(1.0, elapsed)
            print(f"  [CHECKPOINT] {len(results)}/{total_samples} images evaluated ({rate:.1f} imgs/s, {len(results)/total_samples*100:.1f}%)")

    # Save final results
    with open(RESULTS_FILE, "w") as f:
        json.dump({"total_samples": total_samples, "results": results}, f, indent=2)
    print(f"\n[DONE] Full benchmark evaluation results persisted to {RESULTS_FILE}")
    return results

def compute_statistics(results=None):
    if results is None:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r") as f:
                data = json.load(f)
                results = data.get("results", [])
        elif os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as f:
                data = json.load(f)
                results = data.get("results", [])
        else:
            print("[FAIL] No results file found to compute statistics.")
            return None

    class_names = get_class_list()
    num_classes = len(class_names)
    cls_idx = {name: i for i, name in enumerate(class_names)}

    total_count = len(results)
    if total_count == 0:
        print("[WARN] Results list is empty.")
        return None

    # Construct 15x15 confusion matrix
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for r in results:
        t_i = cls_idx[r["true_class"]]
        p_i = cls_idx[r["pred_class"]]
        cm[t_i, p_i] += 1

    top1_correct = sum(1 for r in results if r["is_top1_correct"])
    top3_correct = sum(1 for r in results if r["is_top3_correct"])
    top1_acc = (top1_correct / total_count) * 100.0
    top3_acc = (top3_correct / total_count) * 100.0

    # Per-class metrics
    class_stats = {}
    sensitivities = []
    specificities = []
    precisions = []
    f1s = []

    for i, cls in enumerate(class_names):
        tp = int(cm[i, i])
        fn = int(np.sum(cm[i, :]) - tp)
        fp = int(np.sum(cm[:, i]) - tp)
        tn = int(np.sum(cm) - (tp + fn + fp))

        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        specificity = (tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        sensitivities.append(recall)
        specificities.append(specificity)
        precisions.append(precision)
        f1s.append(f1)

        class_stats[cls] = {
            "n_samples": int(np.sum(cm[i, :])),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "sensitivity": round(recall * 100.0, 2),
            "specificity": round(specificity * 100.0, 2),
            "precision": round(precision * 100.0, 2),
            "f1_score": round(f1 * 100.0, 2)
        }

    macro_sensitivity = float(np.mean(sensitivities) * 100.0)
    macro_specificity = float(np.mean(specificities) * 100.0)
    macro_precision = float(np.mean(precisions) * 100.0)
    macro_f1 = float(np.mean(f1s) * 100.0)

    # Trichometry correlations
    confs = np.array([r["confidence"] for r in results])
    erythemas = np.array([r["erythema_pct"] for r in results])
    flakiness = np.array([r["flakiness_pct"] for r in results])
    exposures = np.array([r["scalp_exposure_pct"] for r in results])
    health_scores = np.array([r["health_score"] for r in results])

    def calc_pearson(x, y):
        if np.std(x) == 0 or np.std(y) == 0:
            return 0.0
        return float(np.corrcoef(x, y)[0, 1])

    r_erythema = calc_pearson(confs, erythemas)
    r_flakiness = calc_pearson(confs, flakiness)
    r_exposure = calc_pearson(confs, exposures)
    r_health = calc_pearson(confs, health_scores)

    summary = {
        "total_samples": total_count,
        "num_classes": num_classes,
        "top1_accuracy": round(top1_acc, 2),
        "top3_accuracy": round(top3_acc, 2),
        "macro_sensitivity": round(macro_sensitivity, 2),
        "macro_specificity": round(macro_specificity, 2),
        "macro_precision": round(macro_precision, 2),
        "macro_f1": round(macro_f1, 2),
        "confusion_matrix": cm.tolist(),
        "class_stats": class_stats,
        "correlations": {
            "confidence_vs_erythema": round(r_erythema, 4),
            "confidence_vs_flakiness": round(r_flakiness, 4),
            "confidence_vs_scalp_exposure": round(r_exposure, 4),
            "confidence_vs_health_score": round(r_health, 4)
        }
    }

    # Print formatted clinical statistics table
    print("\n" + "=" * 92)
    print("SCALED CLINICAL BENCHMARK (2,250 COHORT): PER-CLASS PERFORMANCE MATRIX")
    print("=" * 92)
    print(f"{'Condition Class':26s} | {'N':4s} | {'Sensitivity':11s} | {'Specificity':11s} | {'Precision':9s} | {'F1-Score':8s}")
    print("-" * 92)
    for cls in class_names:
        cs = class_stats[cls]
        print(f"{cls:26s} | {cs['n_samples']:4d} | {cs['sensitivity']:9.2f}% | {cs['specificity']:9.2f}% | {cs['precision']:7.2f}% | {cs['f1_score']:6.2f}%")
    print("-" * 92)
    print(f"{'MACRO AVERAGE':26s} | {total_count:4d} | {macro_sensitivity:9.2f}% | {macro_specificity:9.2f}% | {macro_precision:7.2f}% | {macro_f1:6.2f}%")
    print("=" * 92)
    print(f"Top-1 Clinical Accuracy : {top1_acc:.2f}% ({top1_correct}/{total_count})")
    print(f"Top-3 Diagnostic Recall : {top3_acc:.2f}% ({top3_correct}/{total_count})")
    print(f"Trichometry Correlations: Erythema r={r_erythema:+.3f}, Flakiness r={r_flakiness:+.3f}, Exposure r={r_exposure:+.3f}, Health r={r_health:+.3f}")
    print("=" * 92 + "\n")

    summary_file = os.path.join(BASE_DIR, "scripts", "benchmark_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary metrics saved to {summary_file}")

    return summary

def main():
    parser = argparse.ArgumentParser(description="Evaluate 2,250-Image Scaled Clinical Benchmark Cohort.")
    parser.add_argument("--dry-run", action="store_true", help="Run rapid evaluation on 2 images per class (30 total) to verify pipeline.")
    parser.add_argument("--summary-only", action="store_true", help="Compute and print metrics from existing results/checkpoint.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of images per class.")
    parser.add_argument("--no-resume", action="store_true", help="Start evaluation from scratch ignoring existing checkpoint.")
    args = parser.parse_args()

    if args.summary_only:
        summary = compute_statistics()
        if summary is None:
            print("[INFO] No prior results found. Running dry-run to generate summary data...")
            res = run_batched_evaluation(max_per_class=2, resume=False)
            compute_statistics(res)
        return

    if args.dry_run:
        print("[DRY-RUN] Executing verification test with 2 images per class (30 images total)...")
        res = run_batched_evaluation(max_per_class=2, batch_size=16, resume=False)
        compute_statistics(res)
        print("[SUCCESS] Dry-run evaluation completed without errors.")
        return

    # Full evaluation
    res = run_batched_evaluation(max_per_class=args.limit, resume=(not args.no_resume))
    compute_statistics(res)

if __name__ == "__main__":
    main()
