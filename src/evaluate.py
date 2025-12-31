"""Evaluate model on validation set: simple TP/FP/FN at IoU>=0.5 and compute precision/recall/F1.
Usage:
  python src/evaluate.py --model runs/detect/train2/weights/best.pt --images data/dataset/images/val --labels data/dataset/labels/val --out outputs/eval.csv
"""
import argparse
import csv
import os
from ultralytics import YOLO
import numpy as np


def read_yolo_boxes(txt_path, img_w, img_h):
    boxes = []
    if not os.path.exists(txt_path):
        return boxes
    with open(txt_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls = int(parts[0])
            cx, cy, w, h = map(float, parts[1:5])
            x1 = (cx - w/2) * img_w
            y1 = (cy - h/2) * img_h
            x2 = (cx + w/2) * img_w
            y2 = (cy + h/2) * img_h
            boxes.append([x1, y1, x2, y2])
    return boxes


def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)


def evaluate(model_path, images_dir, labels_dir, out_csv, iou_thr=0.5, conf_thr=0.25):
    model = YOLO(model_path)
    images = []
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            images.append(os.path.join(images_dir, file))

    tp = 0
    fp = 0
    fn = 0

    rows = []
    for img_path in images:
        res = model.predict(source=img_path, conf=conf_thr, save=False)
        r = res[0]
        preds = []
        for box in r.boxes:
            xyxy = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            preds.append((xyxy, conf))

        import cv2
        img = cv2.imread(img_path)
        h, w = img.shape[:2]
        gt_boxes = read_yolo_boxes(os.path.join(labels_dir, os.path.splitext(os.path.basename(img_path))[0] + '.txt'), w, h)

        matched_gt = set()
        for pbox, conf in preds:
            matched = False
            for i, gt in enumerate(gt_boxes):
                if i in matched_gt:
                    continue
                if iou(pbox, gt) >= iou_thr:
                    tp += 1
                    matched = True
                    matched_gt.add(i)
                    break
            if not matched:
                fp += 1
        fn += (len(gt_boxes) - len(matched_gt))

        rows.append({'image': os.path.basename(img_path), 'predictions': len(preds), 'gt': len(gt_boxes)})

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['image', 'predictions', 'gt'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        writer.writerow({'image': 'SUMMARY', 'predictions': f'precision={precision:.3f}', 'gt': f'recall={recall:.3f}, f1={f1:.3f}'})

    print(f"Evaluation complete. Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}. Results saved to {out_csv}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--images', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--out', default='outputs/eval.csv')
    args = parser.parse_args()
    evaluate(args.model, args.images, args.labels, args.out)
