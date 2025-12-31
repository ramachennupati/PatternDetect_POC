"""Simple augmentation: horizontal flip images and adjust YOLO-format labels (cx -> 1 - cx)
Usage:
  python src/augment_flip.py --src data/dataset/images/train --labels data/dataset/labels/train --out images_aug
This will create augmented images and labels under the same folder named with suffix `_flip`.
"""
import argparse
import cv2
import os
from pathlib import Path


def flip_yolo_label_line(line):
    parts = line.strip().split()
    if len(parts) < 5:
        return line
    cls = parts[0]
    cx = float(parts[1])
    cy = float(parts[2])
    w = parts[3]
    h = parts[4]
    cx_flipped = 1.0 - cx
    return f"{cls} {cx_flipped:.6f} {cy:.6f} {w} {h}"


def main(images_dir, labels_dir):
    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)
    out_images_dir = images_dir.parent / (images_dir.name + '_flip')
    out_labels_dir = labels_dir.parent / (labels_dir.name + '_flip')
    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    for img_path in images_dir.glob('*.jpg'):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        flipped = cv2.flip(img, 1)
        out_img_name = img_path.stem + '_flip' + img_path.suffix
        cv2.imwrite(str(out_images_dir / out_img_name), flipped)

        label_path = labels_dir / (img_path.stem + '.txt')
        out_label_path = out_labels_dir / (img_path.stem + '_flip.txt')
        if label_path.exists():
            lines = label_path.read_text().strip().splitlines()
            flipped_lines = [flip_yolo_label_line(l) for l in lines if l.strip()]
            out_label_path.write_text('\n'.join(flipped_lines))

    print(f"Augmented images written to {out_images_dir}; labels to {out_labels_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True, help='images folder')
    parser.add_argument('--labels', required=True, help='labels folder')
    args = parser.parse_args()
    main(args.src, args.labels)
