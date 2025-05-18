import json
from pathlib import Path


_coco_cache = {}


def load_coco_paths_from_json(json_path):
    """
    Returns (image_dir, annotation_file). Assumes COCO format.
    If paths are not available in JSON, uses fallback logic.
    """
    path = Path(json_path)
    if not path.exists():
        return '', ''

    with open(path, 'r') as f:
        data = json.load(f)

    # Optional: check for custom keys like "image_path"
    image_path = data.get('image_path', '')
    annotation_file = str(path.resolve())

    if image_path:
        image_path = str((path.parent / image_path).resolve())
    else:
        image_path = str(path.parent.resolve())

    return Path(image_path), Path(annotation_file)


def load_coco_annotations(image_filename, annotation_json_file):
    global _coco_cache
    annotation_json_file = Path(annotation_json_file)
    image_filename = Path(image_filename).name

    if annotation_json_file.is_dir():
        # Try to find a .json file in this directory
        json_files = list(annotation_json_file.glob("*.json"))
        if json_files:
            annotation_json_file = json_files[0]
        else:
            return []

    if annotation_json_file not in _coco_cache:
        if not annotation_json_file.exists():
            return []
        with open(annotation_json_file, 'r') as f:
            coco = json.load(f)
        _coco_cache[annotation_json_file] = coco
    else:
        coco = _coco_cache[annotation_json_file]

    image_id = None
    for img in coco.get('images', []):
        if img.get('file_name') == image_filename:
            image_id = img['id']
            break

    if image_id is None:
        return []

    annotations = []
    for ann in coco.get('annotations', []):
        if ann.get('image_id') == image_id:
            cls_id = ann['category_id']
            bbox = ann['bbox']  # x, y, width, height
            annotations.append([cls_id] + bbox)

    return annotations