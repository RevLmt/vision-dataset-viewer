# yolo_utils.py
import os

def load_yolo_annotations(annotation_file, img_width, img_height):
    boxes = []
    if not os.path.exists(annotation_file):
        return boxes

    with open(annotation_file, 'r') as f:
        for line in f.readlines():
            cls, x, y, w, h = map(float, line.strip().split())
            # Convert normalized coords to pixels
            x1 = int((x - w / 2) * img_width)
            y1 = int((y - h / 2) * img_height)
            x2 = int((x + w / 2) * img_width)
            y2 = int((y + h / 2) * img_height)
            boxes.append((cls, x1, y1, x2, y2))
    return boxes
