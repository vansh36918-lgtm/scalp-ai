#!/usr/bin/env python3
"""
generate_benchmark_charts.py
Phase 09: Scaled Clinical Cohort Benchmark (150 images/class = 2,250 total)

Generates publication-quality clinical benchmark visualization charts:
1. 15x15 Confusion Matrix Heatmap (confusion_matrix_scaled_2250.png)
2. Per-Class Sensitivity vs Specificity Diagnostic Radar/Bar Chart (clinical_metrics_2250.png)
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SUMMARY_FILE = os.path.join(BASE_DIR, "scripts", "benchmark_summary.json")
RESULTS_FILE = os.path.join(BASE_DIR, "scripts", "benchmark_results.json")
ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\c154bd78-de80-4bc0-a973-1cda8a9d23bd"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "scalp_site.settings"
import django
django.setup()
from detector.ml_model import _load

def generate_charts():
    print("=" * 70)
    print("GENERATING SCALED CLINICAL BENCHMARK CHARTS & VISUALIZATIONS")
    print("=" * 70)

    if not os.path.exists(SUMMARY_FILE):
        print(f"[FAIL] Summary file not found: {SUMMARY_FILE}")
        sys.exit(1)

    with open(SUMMARY_FILE, "r") as f:
        summary = json.load(f)

    _, _, class_names = _load()
    cm = np.array(summary["confusion_matrix"])
    n_classes = len(class_names)
    total_samples = summary["total_samples"]

    # 1. Publication-Quality 15x15 Confusion Matrix Heatmap
    fig, ax = plt.subplots(figsize=(14, 13), dpi=200)
    cmap = plt.cm.Blues
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label("Sample Classification Count", fontsize=11, fontweight="semibold", labelpad=12)

    ax.set_xticks(np.arange(n_classes))
    ax.set_yticks(np.arange(n_classes))
    
    clean_labels = [name.replace("_", " ").title() for name in class_names]
    ax.set_xticklabels(clean_labels, rotation=45, ha="right", fontsize=10, fontweight="medium")
    ax.set_yticklabels(clean_labels, fontsize=10, fontweight="medium")

    ax.set_xlabel("Predicted Diagnostic Class", fontsize=12, fontweight="bold", labelpad=12)
    ax.set_ylabel("True Pathological Ground Truth", fontsize=12, fontweight="bold", labelpad=12)
    ax.set_title(
        f"ScalpAI Clinical Validation: 15-Class Confusion Matrix\n"
        f"Evaluated on N={total_samples} Unseen Clinical Images | Top-1 Accuracy: {summary['top1_accuracy']}%",
        fontsize=14, fontweight="bold", pad=20
    )

    # Annotate numbers in cells
    thresh = cm.max() / 2.0 if cm.max() > 0 else 1.0
    for i in range(n_classes):
        for j in range(n_classes):
            val = cm[i, j]
            color = "white" if val > thresh else "#1e293b"
            ax.text(j, i, format(val, "d"),
                    ha="center", va="center",
                    color=color, fontsize=9, fontweight="bold" if i == j else "normal")

    plt.tight_layout()
    
    out_cm_local = os.path.join(BASE_DIR, "scripts", "confusion_matrix_scaled_2250.png")
    out_cm_static = os.path.join(BASE_DIR, "static", "images", "confusion_matrix_scaled_2250.png")
    out_cm_artifact = os.path.join(ARTIFACT_DIR, "confusion_matrix_scaled_2250.png")

    plt.savefig(out_cm_local)
    if os.path.exists(os.path.dirname(out_cm_static)):
        plt.savefig(out_cm_static)
    if os.path.exists(ARTIFACT_DIR):
        plt.savefig(out_cm_artifact)
    plt.close()
    print(f"[OK] Saved Confusion Matrix heatmap to {out_cm_local}")

    # 2. Per-Class Diagnostic Performance Bar Chart (Sensitivity & Specificity)
    class_stats = summary["class_stats"]
    sensitivities = [class_stats[c]["sensitivity"] for c in class_names]
    specificities = [class_stats[c]["specificity"] for c in class_names]
    f1_scores = [class_stats[c]["f1_score"] for c in class_names]

    x = np.arange(n_classes)
    width = 0.28

    fig, ax = plt.subplots(figsize=(16, 7), dpi=200)
    rects1 = ax.bar(x - width, sensitivities, width, label="Sensitivity (Recall)", color="#0284c7")
    rects2 = ax.bar(x, specificities, width, label="Specificity", color="#10b981")
    rects3 = ax.bar(x + width, f1_scores, width, label="F1-Score", color="#8b5cf6")

    ax.set_ylabel("Diagnostic Percentage (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Per-Class Diagnostic Sensitivity, Specificity & F1-Score (N={total_samples} Cohort)\n"
        f"Macro Sensitivity: {summary['macro_sensitivity']}% | Macro Specificity: {summary['macro_specificity']}% | Macro F1: {summary['macro_f1']}%",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xticks(x)
    ax.set_xticklabels(clean_labels, rotation=40, ha="right", fontsize=9.5)
    ax.set_ylim(0, 115)
    ax.axhline(90, color="#ef4444", linestyle="--", alpha=0.7, label="90% Clinical Threshold")
    ax.legend(loc="lower right", framealpha=0.9, fontsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    plt.tight_layout()
    out_metrics_local = os.path.join(BASE_DIR, "scripts", "clinical_metrics_2250.png")
    out_metrics_static = os.path.join(BASE_DIR, "static", "images", "clinical_metrics_2250.png")
    out_metrics_artifact = os.path.join(ARTIFACT_DIR, "clinical_metrics_2250.png")

    plt.savefig(out_metrics_local)
    if os.path.exists(os.path.dirname(out_metrics_static)):
        plt.savefig(out_metrics_static)
    if os.path.exists(ARTIFACT_DIR):
        plt.savefig(out_metrics_artifact)
    plt.close()
    print(f"[OK] Saved Clinical Metrics bar chart to {out_metrics_local}")

    print("\nBenchmark visualization generation finished successfully!")

if __name__ == "__main__":
    generate_charts()
