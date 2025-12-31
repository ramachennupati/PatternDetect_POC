"""Generate synthetic sample images for testing the detection/demo.

This script creates a few images with simple shapes and 'patterns' (rectangles with hashed fills)
and writes a small template image that can be used for template matching tests.

Usage:
    python scripts/generate_samples.py --out data/samples --count 3

"""
from PIL import Image, ImageDraw, ImageFilter
import os
import argparse
import random

PATTERN_COLOR = (30, 144, 255)
BG_COLOR = (235, 235, 235)
TEMPLATE_SIZE = (120, 60)


def draw_pattern(draw, x, y, w, h, spacing=6):
    """Draw a simple striped pattern inside the rectangle to simulate a feature."""
    draw.rectangle([x, y, x + w, y + h], outline=(10, 10, 10), width=2, fill=None)
    # diagonal stripes
    for i in range(-h, w, spacing):
        draw.line([(x + i, y), (x + i + h, y + h)], fill=PATTERN_COLOR, width=3)


def create_image(path, size=(640, 480), n_patterns=3):
    img = Image.new('RGB', size, BG_COLOR)
    draw = ImageDraw.Draw(img)

    for i in range(n_patterns):
        w = random.randint(80, 220)
        h = random.randint(40, 160)
        x = random.randint(10, size[0] - w - 10)
        y = random.randint(10, size[1] - h - 10)
        draw_pattern(draw, x, y, w, h, spacing=random.randint(6, 12))
        # add a small label rectangle to simulate an object's corner
        draw.rectangle([x + 3, y + 3, x + 30, y + 20], fill=(200, 60, 60))

    # optional blur to make it slightly more realistic
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save(path, quality=90)


def create_template(path):
    # simple pattern matching template (striped rectangle)
    img = Image.new('RGB', TEMPLATE_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_pattern(draw, 4, 4, TEMPLATE_SIZE[0] - 8, TEMPLATE_SIZE[1] - 8, spacing=8)
    img.save(path, quality=90)


def main(out_dir='data/samples', count=3):
    os.makedirs(out_dir, exist_ok=True)
    for i in range(1, count + 1):
        path = os.path.join(out_dir, f'sample{i}.jpg')
        create_image(path)
        print('Wrote', path)

    template_path = os.path.join(out_dir, 'template.png')
    create_template(template_path)
    print('Wrote template', template_path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='data/samples')
    p.add_argument('--count', type=int, default=3)
    args = p.parse_args()
    main(out_dir=args.out, count=args.count)
