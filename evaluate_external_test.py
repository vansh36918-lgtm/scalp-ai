import os
import sys
import glob
from PIL import Image

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scalp_site.settings")
import django
django.setup()

from detector.ml_model import predict_image

test_dir = os.path.join("..", "dataset", "external_test")
if not os.path.exists(test_dir):
    test_dir = os.path.join("dataset", "external_test")

classes = [d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]

total = 0
correct = 0

class_stats = {}

print(f"{'True Class':<25} | {'Predicted Class':<25} | {'Confidence':<10} | {'Result'}", flush=True)
print("-" * 75, flush=True)

for cls in sorted(classes):
    cls_folder = os.path.join(test_dir, cls)
    images = glob.glob(os.path.join(cls_folder, "*.*"))
    class_stats[cls] = {"total": 0, "correct": 0, "failures": []}
    
    for img_path in sorted(images):
        if not img_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        img_name = os.path.basename(img_path)
        img = Image.open(img_path)
        
        label, conf, scores, gradcam, urgency, metrics, treatment = predict_image(img, enable_tta=True)
        
        is_correct = (label == cls)
        total += 1
        class_stats[cls]["total"] += 1
        
        if is_correct:
            correct += 1
            class_stats[cls]["correct"] += 1
        else:
            class_stats[cls]["failures"].append({
                "file": img_name,
                "pred": label,
                "conf": conf,
                "flakiness": metrics["flakiness_pct"],
                "erythema": metrics["erythema_pct"]
            })
            
        status = "[PASS] CORRECT" if is_correct else "[FAIL] INCORRECT"
        print(f"{cls:<25} | {label:<25} | {conf:>6.2f}%    | {status}", flush=True)

acc = (correct / total * 100) if total > 0 else 0
print("=" * 75, flush=True)
print(f"Overall External Test Set Accuracy: {correct}/{total} correct ({acc:.2f}% accuracy)", flush=True)
print("=" * 75, flush=True)

print("\n--- Per-Class Accuracy Breakdown & Failure Analysis ---", flush=True)
for cls, stats in sorted(class_stats.items()):
    cls_acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"* {cls:<25}: {stats['correct']}/{stats['total']} ({cls_acc:.1f}%)", flush=True)
    if stats['failures']:
        for fail in stats['failures']:
            print(f"    - Flaw/Misclassification: File '{fail['file']}' predicted as '{fail['pred']}' (Conf: {fail['conf']}%, Flakiness: {fail['flakiness']}%, Erythema: {fail['erythema']}%)", flush=True)
