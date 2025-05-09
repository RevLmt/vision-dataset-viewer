import os
import yaml

def load_class_names(yaml_path):
    """
    Load class names from a YOLO YAML config file.
    Returns a list where the index corresponds to the class ID.
    """
    if not os.path.exists(yaml_path):
        return []

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    if isinstance(data.get('names'), dict):
        # If names is a dictionary: {0: 'person', 1: 'car'}
        names_dict = data['names']
        class_names = [names_dict[i] for i in sorted(names_dict.keys())]
    elif isinstance(data.get('names'), list):
        class_names = data['names']
    else:
        class_names = []

    return class_names


def load_yolo_annotations(annotation_file, img_width, img_height, class_names=None):
    """
    Load YOLO-format bounding boxes and optionally convert class IDs to names.

    Returns:
        boxes (list of tuples): [(class_id or class_name, x1, y1, x2, y2), ...]
    """
    boxes = []
    if not os.path.exists(annotation_file):
        return boxes

    with open(annotation_file, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls_id = int(float(parts[0]))
            x, y, w, h = map(float, parts[1:5])
            x1 = int((x - w / 2) * img_width)
            y1 = int((y - h / 2) * img_height)
            x2 = int((x + w / 2) * img_width)
            y2 = int((y + h / 2) * img_height)

            cls = class_names[cls_id] if class_names and cls_id < len(class_names) else cls_id
            boxes.append((cls, x1, y1, x2, y2))

    return boxes
