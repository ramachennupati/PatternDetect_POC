"""Pattern matching demo: template matching + ORB feature matching
Usage:
  python src/pattern_matching.py --image data/sample1.jpg --template data/template.png --out outputs/pattern_match.jpg --orb_out outputs/orb_matches.jpg
"""
import argparse
import cv2
import numpy as np
from utils import ensure_dir, save_image


def template_match_demo(image_path, template_path, out_path):
    img = cv2.imread(image_path)
    tpl = cv2.imread(template_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)

    # ensure template is not larger than image; if so, scale it down
    ih, iw = img_gray.shape
    th, tw = tpl_gray.shape
    if th > ih or tw > iw:
        scale = min(ih / th * 0.9, iw / tw * 0.9)
        new_w = max(1, int(tpl_gray.shape[1] * scale))
        new_h = max(1, int(tpl_gray.shape[0] * scale))
        tpl_gray = cv2.resize(tpl_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        tpl = cv2.resize(tpl, (new_w, new_h), interpolation=cv2.INTER_AREA)

    res = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    h, w = tpl_gray.shape
    bottom_right = (top_left[0] + w, top_left[1] + h)

    out = img.copy()
    cv2.rectangle(out, top_left, bottom_right, (0, 255, 0), 3)
    save_image(out_path, out)
    print(f"Template match result saved to {out_path}; score={max_val:.3f}")


def orb_match_demo(image_path, template_path, out_path, max_matches=40):
    img = cv2.imread(image_path)
    tpl = cv2.imread(template_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(1000)
    kp1, des1 = orb.detectAndCompute(tpl_gray, None)
    kp2, des2 = orb.detectAndCompute(img_gray, None)

    if des1 is None or des2 is None:
        print('No descriptors found for ORB matching')
        return

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)[:max_matches]

    match_img = cv2.drawMatches(tpl, kp1, img, kp2, matches, None, flags=2)
    save_image(out_path, match_img)
    print(f"ORB matching result saved to {out_path}; matches={len(matches)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    parser.add_argument('--template', required=True)
    parser.add_argument('--out', default='outputs/pattern_match.jpg')
    parser.add_argument('--orb_out', default='outputs/orb_matches.jpg')
    args = parser.parse_args()

    template_match_demo(args.image, args.template, args.out)
    orb_match_demo(args.image, args.template, args.orb_out)
