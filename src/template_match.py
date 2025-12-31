import argparse
import cv2
import numpy as np
from utils import ensure_dir, save_image


def template_match(image_path: str, template_path: str, out_path: str, method=cv2.TM_CCOEFF_NORMED):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    tpl = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    if tpl is None:
        raise ValueError(f"Could not read template: {template_path}")

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, tpl_gray, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc if method in [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED] else min_loc
    h, w = tpl_gray.shape
    bottom_right = (top_left[0] + w, top_left[1] + h)

    out = img.copy()
    cv2.rectangle(out, top_left, bottom_right, (0, 255, 0), 3)

    ensure_dir(out_path and out_path.rsplit('\\', 1)[0] or '.')
    save_image(out_path, out)
    print(f"Saved template match output to {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, required=True)
    parser.add_argument('--template', type=str, required=True)
    parser.add_argument('--output', type=str, default='outputs/template_out.jpg')
    args = parser.parse_args()

    template_match(args.image, args.template, args.output)
