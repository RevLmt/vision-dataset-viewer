import os
import json


def load_coco_annotations(json_path, image_filename):
    """
    Load bounding boxes for a single image from a COCO-format JSON annotation file.

    Args:
        json_path (str): Path to the COCO annotation .json file.
        image_filename (str): Name of the image file to extract annotations for.

    Returns:
        boxes (list of tuples): List of (class_id or class_name, x1, y1, x2, y2)
    """
    if not os.path.exists(json_path):
        return []

    with open(json_path, 'r') as f:
        coco = json.load(f)

    # Create image_id lookup
    filename_to_id = {img['file_name']: img['id'] for img in coco['images']}
    image_id = filename_to_id.get(image_filename)
    if image_id is None:
        return []

    # Create category_id to name lookup
    category_id_to_name = {cat['id']: cat['name'] for cat in coco['categories']}

    boxes = []
    for ann in coco['annotations']:
        if ann['image_id'] != image_id:
            continue
        if ann.get('iscrowd', 0) == 1:
            continue

        x, y, w, h = ann['bbox']
        x1 = int(x)
        y1 = int(y)
        x2 = int(x + w)
        y2 = int(y + h)
        class_name = category_id_to_name.get(ann['category_id'], str(ann['category_id']))
        boxes.append((class_name, x1, y1, x2, y2))

    return boxes
