#!/usr/bin/env python3
"""Traffic light classifier for the FRDM-IMX93 (or any Linux host).

Standalone port of Traffic_Light_Classifier.ipynb: same preprocessing,
features and decision rule, but with no Jupyter or matplotlib dependency,
so it runs on the board with only python3, OpenCV and NumPy.

Usage:
  traffic_light_classifier.py eval  <dataset_dir>     # e.g. traffic_light_images/test
  traffic_light_classifier.py image <file> [<file>...]
  traffic_light_classifier.py camera [--device 0] [--roi x,y,w,h]
"""
import argparse
import glob
import os
import sys
import time

import cv2
import numpy as np

LABELS = ["red", "yellow", "green"]


def load_rgb(path):
    """Read an image as RGB uint8 (matches matplotlib.image.imread for JPEGs)."""
    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    if bgr is None:
        return None
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def standardize_input(image):
    """Crop the border and resize to 32x32, as in the notebook."""
    row_crop, col_crop = 5, 8
    cropped = image[row_crop:-row_crop, col_crop:-col_crop, :]
    return cv2.resize(cropped, (32, 32))


def create_feature(rgb_image):
    """Average V-channel brightness in the red, yellow and green bands."""
    v = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)[:, :, 2].astype(np.float64)
    area = 32 * 32
    red = np.sum(v[:15, 5:25]) / area
    yellow = np.sum(v[13:18, 5:25]) / area
    green = np.sum(v[17:, 5:25]) / area
    return [red, yellow, green]


def estimate_label(rgb_image):
    """Return 'red', 'yellow' or 'green' for a standardized 32x32 RGB image."""
    r, y, g = create_feature(rgb_image)
    if r > y and r > g:
        return "red"
    if g > r and g > y:
        return "green"
    return "yellow"


def classify(rgb_image):
    return estimate_label(standardize_input(rgb_image))


def cmd_eval(dataset_dir):
    total = correct = red_as_green = 0
    t0 = time.perf_counter()
    for label in LABELS:
        for path in sorted(glob.glob(os.path.join(dataset_dir, label, "*"))):
            img = load_rgb(path)
            if img is None:
                continue
            pred = classify(img)
            total += 1
            correct += pred == label
            red_as_green += label == "red" and pred == "green"
    dt = time.perf_counter() - t0
    if total == 0:
        sys.exit(f"No images found under {dataset_dir}/{{red,yellow,green}}/")
    print(f"Accuracy: {correct / total:.4f}  ({correct}/{total} correct)")
    print(f"Misclassified: {total - correct}   red classified as green: {red_as_green}")
    print(f"Time: {dt:.2f} s total, {1000 * dt / total:.2f} ms per image")


def cmd_image(paths):
    for path in paths:
        img = load_rgb(path)
        if img is None:
            print(f"{path}: cannot read image")
            continue
        print(f"{path}: {classify(img)}")


def cmd_camera(device, roi):
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        sys.exit(f"Cannot open camera {device}")
    print("Press Ctrl-C to stop.")
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                print("Frame grab failed")
                time.sleep(0.5)
                continue
            if roi:
                x, y, w, h = roi
                bgr = bgr[y:y + h, x:x + w]
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            print(classify(rgb), flush=True)
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("eval", help="measure accuracy on a labelled dataset folder")
    e.add_argument("dataset_dir")
    i = sub.add_parser("image", help="classify one or more image files")
    i.add_argument("paths", nargs="+")
    c = sub.add_parser("camera", help="classify live frames from a camera")
    c.add_argument("--device", default="0",
                   help="camera index or device path (default 0)")
    c.add_argument("--roi", help="crop region x,y,w,h around the traffic light")
    a = p.parse_args()

    if a.cmd == "eval":
        cmd_eval(a.dataset_dir)
    elif a.cmd == "image":
        cmd_image(a.paths)
    else:
        dev = int(a.device) if a.device.isdigit() else a.device
        roi = tuple(int(v) for v in a.roi.split(",")) if a.roi else None
        cmd_camera(dev, roi)


if __name__ == "__main__":
    main()
