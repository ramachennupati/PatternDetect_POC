import os


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_image(path, img):
    # img is numpy array (BGR) — use cv2.imwrite where needed
    import cv2
    ensure_dir(os.path.dirname(path))
    cv2.imwrite(path, img)
