import argparse
import os
import cv2
from ultralytics import YOLO

from utils import ensure_dir, save_image


def run_detection(source: str, out_path: str, conf: float = 0.25):
    model = YOLO('yolov8n.pt')  # downloads the small pre-trained model if missing
    results = model.predict(source=source, conf=conf, save=False)

    # results is a list (one element per image)
    r = results[0]

    # r.plot() returns an annotated image (RGB numpy array)
    annotated = r.plot()

    # ultralytics plot returns RGB; convert to BGR for OpenCV saving
    annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

    ensure_dir(os.path.dirname(out_path) or '.')
    save_image(out_path, annotated_bgr)
    print(f"Saved annotated image to {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True, help='Image or folder of images')
    parser.add_argument('--output', type=str, required=False, default='outputs/detect_out.jpg')
    parser.add_argument('--conf', type=float, default=0.25)
    args = parser.parse_args()

    run_detection(args.source, args.output, args.conf)
