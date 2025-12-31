"""Auto-annotate images using pretrained YOLO and write YOLO-format label files.
Usage:
    python src/auto_annotate.py --images data/dataset/images/train --labels data/dataset/labels/train
"""
import argparse
import os
from ultralytics import YOLO
from pathlib import Path


def xyxy_to_yolo(xyxy, img_w, img_h):
    x1, y1, x2, y2 = xyxy
    cx = (x1 + x2) / 2.0 / img_w
    cy = (y1 + y2) / 2.0 / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    return cx, cy, w, h


def main(images_dir, labels_dir, conf=0.25, model_path='yolov8n.pt'):
    model = YOLO(model_path)
    os.makedirs(labels_dir, exist_ok=True)

    images = list(Path(images_dir).glob('*.jpg')) + list(Path(images_dir).glob('*.png'))
    if not images:
        print('No images found in', images_dir)
        return

    for img_path in images:
        print('Annotating', img_path.name)
        res = model.predict(source=str(img_path), conf=conf, save=False)
        r = res[0]
        img = r.orig_img
        h, w = img.shape[:2]
        label_path = Path(labels_dir) / (img_path.stem + '.txt')
        lines = []
        for box in r.boxes:
            # Map all detections to a single class (0) for quick fine-tuning PoC
            cls = 0
            xyxy = box.xyxy[0].tolist()
            cx, cy, bw, bh = xyxy_to_yolo(xyxy, w, h)
            lines.append(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
        label_path.write_text('\n'.join(lines))
    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--conf', type=float, default=0.25)
    args = parser.parse_args()
    main(args.images, args.labels, args.conf)
