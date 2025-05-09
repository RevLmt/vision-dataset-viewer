# import os
# import cv2
# import numpy as np
# from PyQt5 import QtWidgets, QtGui, QtCore
# import pyqtgraph as pg
# from yolo_utils import load_yolo_annotations, load_class_names
# from coco_utils import load_coco_annotations


# class DatasetViewer(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Dataset Viewer")
#         self.resize(900, 700)

#         # Internal state
#         self.image_dir = None
#         self.label_dir = None
#         self.yaml_path = None
#         self.image_files = []
#         self.index = 0
#         self.annotation_format = 'YOLO'  # Default format
#         self.class_names = []

#         # Layouts
#         layout = QtWidgets.QVBoxLayout(self)
#         self.setLayout(layout)

#         # === Annotation format selector ===
#         self.format_selector = QtWidgets.QComboBox()
#         self.format_selector.addItems(['COCO', 'YOLO'])
#         self.format_selector.currentTextChanged.connect(self.on_format_change)

#         layout.addWidget(QtWidgets.QLabel("Annotation Format:"))
#         layout.addWidget(self.format_selector)

#         # === Folder selection rows ===
#         default_path = os.path.expanduser("~/Downloads")

#         image_btn = QtWidgets.QPushButton()
#         image_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
#         image_btn.clicked.connect(self.select_image_folder)

#         label_btn = QtWidgets.QPushButton()
#         label_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
#         label_btn.clicked.connect(self.select_label_folder)

#         self.yaml_btn = QtWidgets.QPushButton()
#         self.yaml_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
#         self.yaml_btn.clicked.connect(self.select_yaml_file)
#         self.yaml_btn.hide()

#         self.image_path_label = QtWidgets.QLineEdit()
#         self.image_path_label.setReadOnly(True)
#         self.image_path_label.setText("No folder selected")

#         self.label_path_label = QtWidgets.QLineEdit()
#         self.label_path_label.setReadOnly(True)
#         self.label_path_label.setText("No folder selected")

#         self.yaml_path_label = QtWidgets.QLineEdit()
#         self.yaml_path_label.setReadOnly(True)
#         self.yaml_path_label.setText("No .yaml file selected")
#         self.yaml_path_label.hide()
#         path_layout_1 = QtWidgets.QHBoxLayout()
#         path_layout_1.addWidget(QtWidgets.QLabel("Image Folder:"))
#         path_layout_1.addWidget(self.image_path_label)
#         path_layout_1.addWidget(image_btn)

#         path_layout_2 = QtWidgets.QHBoxLayout()
#         path_layout_2.addWidget(QtWidgets.QLabel("Label Folder / JSON File:"))
#         path_layout_2.addWidget(self.label_path_label)
#         path_layout_2.addWidget(label_btn)

#         path_layout_3 = QtWidgets.QHBoxLayout()
#         path_layout_3.addWidget(QtWidgets.QLabel("YOLO .yaml File:"))
#         path_layout_3.addWidget(self.yaml_path_label)
#         path_layout_3.addWidget(self.yaml_btn)

#         layout.addLayout(path_layout_1)
#         layout.addLayout(path_layout_2)
#         layout.addLayout(path_layout_3)

#         # === Image Viewer ===
#         self.view = pg.GraphicsLayoutWidget()
#         self.img_item = pg.ImageItem()
#         self.plot = self.view.addPlot()
#         self.plot.addItem(self.img_item)
#         self.plot.setAspectLocked(True)
#         layout.addWidget(self.view)

#         # === Info + Navigation ===
#         self.label = QtWidgets.QLabel("No image loaded")
#         self.prev_btn = QtWidgets.QPushButton("Prev")
#         self.next_btn = QtWidgets.QPushButton("Next")

#         self.prev_btn.clicked.connect(self.prev_image)
#         self.next_btn.clicked.connect(self.next_image)
#         self.prev_btn.setEnabled(False)
#         self.next_btn.setEnabled(False)

#         nav_layout = QtWidgets.QHBoxLayout()
#         nav_layout.addWidget(self.prev_btn)
#         nav_layout.addWidget(self.next_btn)
#         nav_layout.addWidget(self.label)
#         layout.addLayout(nav_layout)

#     def on_format_change(self):
#         is_yolo = self.format_selector.currentText() == 'YOLO'
#         self.yaml_path_label.setVisible(is_yolo)
#         self.yaml_btn.setVisible(is_yolo)
#         self.try_load_dataset()

#     def select_image_folder(self):
#         folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Folder", os.path.expanduser("~/Downloads"))
#         if folder:
#             self.image_dir = folder
#             self.image_path_label.setText(folder)
#             self.try_load_dataset()

#     def select_label_folder(self):
#         if self.format_selector.currentText() == 'COCO':
#             file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select COCO JSON File", os.path.expanduser("~/Downloads"), "JSON Files (*.json)")
#             self.class_names = []
#         else:
#             file = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Label Folder", os.path.expanduser("~/Downloads"))

#         if file:
#             self.label_dir = file
#             self.label_path_label.setText(file)
#             self.try_load_dataset()

#     def select_yaml_file(self):
#         yaml_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select YOLO .yaml File", os.path.expanduser("~/Downloads"), "YAML Files (*.yaml *.yml)")
#         if yaml_path:
#             self.yaml_path = yaml_path
#             self.yaml_path_label.setText(yaml_path)
#             self.class_names = load_class_names(yaml_path)
#             self.try_load_dataset()

#     def try_load_dataset(self):
#         self.annotation_format = self.format_selector.currentText()
#         if self.image_dir and self.label_dir:
#             self.image_files = [f for f in os.listdir(self.image_dir)
#                                 if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
#             self.image_files.sort()
#             self.index = 0
#             if self.image_files:
#                 self.prev_btn.setEnabled(True)
#                 self.next_btn.setEnabled(True)
#                 self.update_view()
#             else:
#                 self.label.setText("No images found in folder.")

#     def update_view(self):
#         image_path = os.path.join(self.image_dir, self.image_files[self.index])
#         img = cv2.imread(image_path)
#         if img is None:
#             self.label.setText("Error loading image.")
#             return
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         img_flipped = np.flipud(img)
#         img_disp = img_flipped.transpose((1, 0, 2))  # flipped image for correct orientation

#         self.img_item.setImage(img_disp, levels=(0, 255))

#         # Clear old boxes
#         for item in self.plot.items[:]:
#             if isinstance(item, QtWidgets.QGraphicsItem) and isinstance(item, QtWidgets.QGraphicsRectItem):
#                 self.plot.removeItem(item)

#         if self.annotation_format == 'YOLO':
#             ann_path = os.path.join(self.label_dir, os.path.splitext(self.image_files[self.index])[0] + '.txt')
#             boxes = load_yolo_annotations(ann_path, img.shape[1], img.shape[0], self.class_names)
#         else:  # COCO
#             boxes = load_coco_annotations(self.label_dir, self.image_files[self.index])

#         for cls, x1, y1, x2, y2 in boxes:
#             y1_flipped = img.shape[0] - y2
#             y2_flipped = img.shape[0] - y1
#             rect = QtWidgets.QGraphicsRectItem(QtCore.QRectF(x1, y1_flipped, x2 - x1, y2_flipped - y1_flipped))
#             rect.setPen(pg.mkPen('r', width=2))
#             self.plot.addItem(rect)

#             # Draw label text
#             text = QtWidgets.QGraphicsTextItem(str(cls))
#             text.setDefaultTextColor(QtGui.QColor('yellow'))
#             text.setPos(x1, y2_flipped + 2)
#             text.setTransform(QtGui.QTransform().scale(1, -1))  # Slightly above the box
#             self.plot.addItem(text)

#         self.label.setText(f"{self.index + 1}/{len(self.image_files)}: {self.image_files[self.index]}")

#     def next_image(self):
#         if self.index < len(self.image_files) - 1:
#             self.index += 1
#             self.update_view()

#     def prev_image(self):
#         if self.index > 0:
#             self.index -= 1
#             self.update_view()


# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     viewer = DatasetViewer()
#     viewer.show()
#     app.exec_()

import os
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
from yolo_utils import load_yolo_annotations, load_class_names
from coco_utils import load_coco_annotations


class DatasetViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Viewer")
        self.resize(900, 700)

        # Internal state
        self.image_dir = None
        self.label_dir = None
        self.yaml_path = None
        self.image_files = []
        self.index = 0
        self.annotation_format = 'YOLO'  # Default format
        self.class_names = []

        # Layouts
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # === Annotation format selector ===
        self.format_selector = QtWidgets.QComboBox()
        self.format_selector.addItems(['COCO', 'YOLO'])
        self.format_selector.currentTextChanged.connect(self.on_format_change)

        layout.addWidget(QtWidgets.QLabel("Annotation Format:"))
        layout.addWidget(self.format_selector)

        # === Folder selection rows ===
        default_path = os.path.expanduser("~/Downloads")

        image_btn = QtWidgets.QPushButton()
        image_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
        image_btn.clicked.connect(self.select_image_folder)

        label_btn = QtWidgets.QPushButton()
        label_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
        label_btn.clicked.connect(self.select_label_folder)

        self.yaml_btn = QtWidgets.QPushButton()
        self.yaml_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
        self.yaml_btn.clicked.connect(self.select_yaml_file)
        self.yaml_btn.hide()

        self.image_path_label = QtWidgets.QLineEdit()
        self.image_path_label.setReadOnly(True)
        self.image_path_label.setText("No folder selected")

        self.label_path_label = QtWidgets.QLineEdit()
        self.label_path_label.setReadOnly(True)
        self.label_path_label.setText("No folder selected")

        self.yaml_path_label = QtWidgets.QLineEdit()
        self.yaml_path_label.setReadOnly(True)
        self.yaml_path_label.setText("No .yaml file selected")
        self.yaml_path_label.hide()
        path_layout_1 = QtWidgets.QHBoxLayout()
        path_layout_1.addWidget(QtWidgets.QLabel("Image Folder:"))
        path_layout_1.addWidget(self.image_path_label)
        path_layout_1.addWidget(image_btn)

        path_layout_2 = QtWidgets.QHBoxLayout()
        path_layout_2.addWidget(QtWidgets.QLabel("Label Folder / JSON File:"))
        path_layout_2.addWidget(self.label_path_label)
        path_layout_2.addWidget(label_btn)

        path_layout_3 = QtWidgets.QHBoxLayout()
        path_layout_3.addWidget(QtWidgets.QLabel("YOLO .yaml File:"))
        path_layout_3.addWidget(self.yaml_path_label)
        path_layout_3.addWidget(self.yaml_btn)

        layout.addLayout(path_layout_1)
        layout.addLayout(path_layout_2)
        layout.addLayout(path_layout_3)

        # === Image Viewer ===
        self.view = pg.GraphicsLayoutWidget()
        self.img_item = pg.ImageItem()
        self.plot = self.view.addPlot()
        self.plot.addItem(self.img_item)
        self.plot.setAspectLocked(True)
        layout.addWidget(self.view)

        # === Info + Navigation ===
        self.label = QtWidgets.QLabel("No image loaded")
        self.prev_btn = QtWidgets.QPushButton("Prev")
        self.next_btn = QtWidgets.QPushButton("Next")

        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

        nav_layout = QtWidgets.QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.label)
        layout.addLayout(nav_layout)

    def on_format_change(self):
        is_yolo = self.format_selector.currentText() == 'YOLO'
        self.yaml_path_label.setVisible(is_yolo)
        self.yaml_btn.setVisible(is_yolo)
        self.try_load_dataset()

    def select_image_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Folder", os.path.expanduser("~/Downloads"))
        if folder:
            self.image_dir = folder
            self.image_path_label.setText(folder)
            self.try_load_dataset()

    def select_label_folder(self):
        if self.format_selector.currentText() == 'COCO':
            file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select COCO JSON File", os.path.expanduser("~/Downloads"), "JSON Files (*.json)")
            self.class_names = []
        else:
            file = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Label Folder", os.path.expanduser("~/Downloads"))

        if file:
            self.label_dir = file
            self.label_path_label.setText(file)
            self.try_load_dataset()

    def select_yaml_file(self):
        yaml_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select YOLO .yaml File", os.path.expanduser("~/Downloads"), "YAML Files (*.yaml *.yml)")
        if yaml_path:
            self.yaml_path = yaml_path
            self.yaml_path_label.setText(yaml_path)
            self.class_names = load_class_names(yaml_path)
            self.try_load_dataset()

    def try_load_dataset(self):
        self.annotation_format = self.format_selector.currentText()
        if self.image_dir and self.label_dir:
            self.image_files = [f for f in os.listdir(self.image_dir)
                                if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            self.image_files.sort()
            self.index = 0
            if self.image_files:
                self.prev_btn.setEnabled(True)
                self.next_btn.setEnabled(True)
                self.update_view()
            else:
                self.label.setText("No images found in folder.")

    def update_view(self):
        image_path = os.path.join(self.image_dir, self.image_files[self.index])
        img = cv2.imread(image_path)
        if img is None:
            self.label.setText("Error loading image.")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_flipped = np.flipud(img)
        img_disp = img_flipped.transpose((1, 0, 2))  # flipped image for correct orientation

        self.img_item.setImage(img_disp, levels=(0, 255))

        # Clear old boxes
        for item in self.plot.items[:]:
            if isinstance(item, QtWidgets.QGraphicsItem) and isinstance(item, QtWidgets.QGraphicsRectItem):
                self.plot.removeItem(item)

        if self.annotation_format == 'YOLO':
            ann_path = os.path.join(self.label_dir, os.path.splitext(self.image_files[self.index])[0] + '.txt')
            boxes = load_yolo_annotations(ann_path, img.shape[1], img.shape[0], self.class_names)
        else:  # COCO
            boxes = load_coco_annotations(self.label_path_label.text(), self.image_files[self.index])

        for cls, x1, y1, x2, y2 in boxes:
            y1_flipped = img.shape[0] - y2
            y2_flipped = img.shape[0] - y1
            rect = QtWidgets.QGraphicsRectItem(QtCore.QRectF(x1, y1_flipped, x2 - x1, y2_flipped - y1_flipped))
            rect.setPen(pg.mkPen('r', width=2))
            self.plot.addItem(rect)

            # Draw label text
            text = QtWidgets.QGraphicsTextItem(str(cls))
            text.setDefaultTextColor(QtGui.QColor('yellow'))
            text.setPos(x1, y2_flipped + 2)
            text.setTransform(QtGui.QTransform().scale(1, -1))  # Slightly above the box
            self.plot.addItem(text)

        self.label.setText(f"{self.index + 1}/{len(self.image_files)}: {self.image_files[self.index]}")

    def next_image(self):
        if self.index < len(self.image_files) - 1:
            self.index += 1
            self.update_view()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_view()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    viewer = DatasetViewer()
    viewer.show()
    app.exec_()






