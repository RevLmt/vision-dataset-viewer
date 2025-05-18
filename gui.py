import os
import cv2
import numpy as np
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
from yolo_utils import load_yolo_annotations, load_class_names, load_yaml_config
from coco_utils import load_coco_annotations, load_coco_paths_from_json


class DatasetViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Viewer")
        self.resize(1000, 800)

        # State
        self.image_files = []
        self.index = 0
        self.annotation_format = 'YOLO'  # Default
        self.class_names = []

        # Layout
        layout = QtWidgets.QVBoxLayout()
        control_layout = QtWidgets.QHBoxLayout()

        # File path inputs
        self.image_dir_edit = QtWidgets.QLineEdit()
        self.label_dir_edit = QtWidgets.QLineEdit()
        image_browse = QtWidgets.QPushButton("Browse")
        label_browse = QtWidgets.QPushButton("Browse")

        image_browse.clicked.connect(self.browse_image_dir)
        label_browse.clicked.connect(self.browse_label_dir)

        image_row = QtWidgets.QHBoxLayout()
        image_row.addWidget(self.image_dir_edit, 1)
        image_row.addWidget(image_browse)

        label_row = QtWidgets.QHBoxLayout()
        label_row.addWidget(self.label_dir_edit, 1)
        label_row.addWidget(label_browse)

        path_container = QtWidgets.QVBoxLayout()

        image_widget = QtWidgets.QWidget()
        image_widget.setLayout(image_row)
        path_container.addWidget(QtWidgets.QLabel("Image Directory:"))
        path_container.addWidget(image_widget)

        label_widget = QtWidgets.QWidget()
        label_widget.setLayout(label_row)
        path_container.addWidget(QtWidgets.QLabel("Label File or Directory (COCO .json or YOLO folder):"))
        path_container.addWidget(label_widget)

        layout.addLayout(path_container)

        # Image viewer
        self.view = pg.ImageView()
        layout.addWidget(self.view)

        # Control buttons
        self.load_btn = QtWidgets.QPushButton("Load Config (YAML/JSON)")
        self.prev_btn = QtWidgets.QPushButton("Previous")
        self.next_btn = QtWidgets.QPushButton("Next")
        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.next_btn)
        layout.addLayout(control_layout)

        self.setLayout(layout)

        # Signals
        self.load_btn.clicked.connect(self.load_config)
        self.prev_btn.clicked.connect(self.show_previous)
        self.next_btn.clicked.connect(self.show_next)

    def browse_image_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if dir_path:
            self.image_dir_edit.setText(dir_path)
            self.refresh_image_list()

    def browse_label_dir(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Label Directory or JSON File")
        if path:
            self.label_dir_edit.setText(path)

    def load_config(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select YAML or JSON", "", "Config Files (*.yaml *.yml *.json)")
        if not file_path:
            return

        ext = Path(file_path).suffix.lower()
        if ext in ['.yaml', '.yml']:
            self.annotation_format = 'YOLO'
            config = load_yaml_config(file_path)
            self.class_names = load_class_names(config.get('names', []))
            if config.get('image_path'):
                self.image_dir_edit.setText(config['image_path'])
            if config.get('label_path'):
                self.label_dir_edit.setText(config['label_path'])
        elif ext == '.json':
            self.annotation_format = 'COCO'
            image_dir, label_path = load_coco_paths_from_json(file_path)
            self.image_dir_edit.setText(str(image_dir))
            self.label_dir_edit.setText(str(label_path))
            self.class_names = []  # Optionally load COCO categories later

        self.refresh_image_list()

    def refresh_image_list(self):
        image_dir = Path(self.image_dir_edit.text())
        if not image_dir.exists():
            return
        self.image_files = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))
        self.image_files.sort()
        self.index = 0
        self.show_image()

    def show_previous(self):
        if self.index > 0:
            self.index -= 1
            self.show_image()

    def show_next(self):
        if self.index < len(self.image_files) - 1:
            self.index += 1
            self.show_image()

    def show_image(self):
        if not self.image_files:
            return

        img_path = self.image_files[self.index]
        image = cv2.imread(str(img_path))
        if image is None:
            return

        annotations = []
        label_dir = Path(self.label_dir_edit.text())
        if self.annotation_format == 'YOLO':
            label_path = label_dir / (img_path.stem + ".txt")
            annotations = load_yolo_annotations(label_path)
        elif self.annotation_format == 'COCO':
            annotations = load_coco_annotations(img_path.name, label_dir)

        drawn_img = self.draw_annotations(image, annotations)
        self.display_image(drawn_img)

    def draw_annotations(self, image, annotations):
        img_h, img_w = image.shape[:2]

        for ann in annotations:
            cls_id = ann[0]
            bbox = ann[1:]
            if self.annotation_format == 'YOLO':
                x_center, y_center, w, h = bbox
                x1 = int((x_center - w / 2) * img_w)
                y1 = int((y_center - h / 2) * img_h)
                x2 = int((x_center + w / 2) * img_w)
                y2 = int((y_center + h / 2) * img_h)
            else:  # COCO
                x1, y1, w, h = bbox
                x2, y2 = x1 + w, y1 + h
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

            color = (0, 255, 0)
            label = self.class_names[cls_id] if cls_id < len(self.class_names) else str(cls_id)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return image

    def display_image(self, image):
        # Resize image to fit view while maintaining aspect ratio
        view_size = self.view.size()
        win_w, win_h = view_size.width(), view_size.height()
        img_h, img_w = image.shape[:2]

        scale = min(win_w / img_w, win_h / img_h)
        resized = cv2.resize(image, (int(img_w * scale), int(img_h * scale)), interpolation=cv2.INTER_AREA)
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        self.view.setImage(rgb_image.transpose(1, 0, 2))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    viewer = DatasetViewer()
    viewer.show()
    app.exec()