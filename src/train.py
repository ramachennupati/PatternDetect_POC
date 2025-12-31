"""Simple training wrapper using Ultralytics YOLOv8
Usage:
    python src/train.py --data data/dataset/dataset.yaml --epochs 5 --device cpu
"""
import argparse
from ultralytics import YOLO


def main(data_yaml, epochs=5, model='yolov8n.pt', device='cpu', name='train'):
    y = YOLO(model)
    y.train(data=data_yaml, epochs=epochs, device=device, imgsz=640, name=name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--model', type=str, default='yolov8n.pt')
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--name', type=str, default='train')
    args = parser.parse_args()
    main(args.data, args.epochs, args.model, args.device, args.name)
