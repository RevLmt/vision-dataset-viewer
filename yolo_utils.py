from pathlib import Path


def load_yolo_annotations(label_path):
    annotations = []
    if not label_path.exists():
        return annotations
    with open(label_path, 'r') as f:
        for line in f.readlines():
            parts = list(map(float, line.strip().split()))
            if len(parts) >= 5:
                cls_id = int(parts[0])
                bbox = parts[1:5]
                annotations.append([cls_id] + bbox)
    return annotations


def load_class_names(names):
    if isinstance(names, list):
        return names
    if isinstance(names, str):
        path = Path(names)
        if path.exists():
            with open(path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
    return []


def load_yaml_config(yaml_path):
    import yaml
    path = Path(yaml_path)
    if not path.exists():
        return {}

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    # Extract key paths with fallback
    image_path = data.get('image_path')
    label_path = data.get('label_path')
    if image_path is not None:
        image_path = str(Path(yaml_path).parent / image_path)
    if label_path is not None:
        label_path = str(Path(yaml_path).parent / label_path)

    return {
        'names': data.get('names', []),
        'image_path': image_path or '',
        'label_path': label_path or ''
    }