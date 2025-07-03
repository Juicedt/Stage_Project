from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QSlider, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

from image_viewer import ImageViewer
from three_d_viewer import ThreeDViewer


class ThreeDViewerWidget(QWidget):
    go_back_to_home = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        viewers_layout = QHBoxLayout()
        viewers_layout.setContentsMargins(0, 0, 0, 0)

        self.three_d_viewer_component = ThreeDViewer(self)
        self.image_viewer_component = ImageViewer(self)

        viewers_layout.addWidget(self.three_d_viewer_component, 1)
        viewers_layout.addWidget(self.image_viewer_component, 1)

        self.main_layout.addLayout(viewers_layout, 3)

        def make_slider(label_text, min_val, max_val, default_val, slot, step=1):
            layout = QHBoxLayout()
            label = QLabel(label_text)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default_val)
            slider.setSingleStep(step)
            slider.valueChanged.connect(slot)
            layout.addWidget(label)
            layout.addWidget(slider)
            return layout, slider

        bottom_controls_layout = QHBoxLayout()

        # --- COLUMN 1: BUTTONS FOR 3D VIEWER ---
        col_1 = QVBoxLayout()
        col_1.setAlignment(Qt.AlignTop)
        self.btn_select_folder = QPushButton("Select Folder")
        self.btn_select_folder.clicked.connect(self._select_folder_and_load_3d_slices)
        self.btn_reset_view_3d = QPushButton("Reset View")
        self.btn_reset_view_3d.clicked.connect(self.reset_view_3d)
        self.btn_invert_colors_3d = QPushButton("Invert Colors")
        self.btn_invert_colors_3d.clicked.connect(self.invert_colors_3d)
        self.btn_grayscale_3d = QPushButton("Grayscale")
        self.btn_grayscale_3d.clicked.connect(self.grayscale_3d)
        self.btn_bg_color_3d = QPushButton("Set BG Color")
        self.btn_bg_color_3d.clicked.connect(self.set_bg_color_3d)
        self.btn_screenshot_3d = QPushButton("Screenshot View")
        self.btn_screenshot_3d.clicked.connect(self.screenshot_3d)

        for btn in [
            self.btn_select_folder, self.btn_reset_view_3d, self.btn_invert_colors_3d,
            self.btn_grayscale_3d, self.btn_bg_color_3d, self.btn_screenshot_3d
        ]:
            col_1.addWidget(btn)

        # --- COLUMN 2: SLIDERS FOR 3D VIEWER ---
        col_2 = QVBoxLayout()
        col_2.setAlignment(Qt.AlignTop)
        layout, self.slider_zspacing_3d =   make_slider("Z-Spacing ", 1, 100, 10, self.set_zspacing_3d)
        col_2.addLayout(layout)
        layout, self.slider_opacity_3d =    make_slider("Opacity   ", 0, 100, 100, self.set_opacity_3d)
        col_2.addLayout(layout)
        layout, self.slider_brightness_3d = make_slider("Brightness", 0, 200, 100, self.set_brightness_3d)
        col_2.addLayout(layout)
        layout, self.slider_contrast_3d =   make_slider("Contrast  ", 0, 200, 100, self.set_contrast_3d)
        col_2.addLayout(layout)
        layout, self.slider_saturation_3d = make_slider("Saturation", 0, 200, 100, self.set_saturation_3d)
        col_2.addLayout(layout)

        # --- COLUMN 3: BUTTONS FOR 2D VIEWER ---
        col_3 = QVBoxLayout()
        col_3.setAlignment(Qt.AlignTop)
        self.btn_select_image = QPushButton("Select Image")
        self.btn_select_image.clicked.connect(self._select_file_and_load_2d_image)
        self.btn_invert_colors_2d = QPushButton("Invert Colors")
        self.btn_invert_colors_2d.clicked.connect(self.invert_colors_2d)
        self.btn_grayscale_2d = QPushButton("Grayscale")
        self.btn_grayscale_2d.clicked.connect(self.grayscale_2d)
        self.btn_bg_color_2d = QPushButton("Set BG Color")
        self.btn_bg_color_2d.clicked.connect(self.set_bg_color_2d)
        self.btn_screenshot_2d = QPushButton("Screenshot View")
        self.btn_screenshot_2d.clicked.connect(self.screenshot_2d)

        for btn in [
            self.btn_select_image, self.btn_invert_colors_2d, self.btn_grayscale_2d,
            self.btn_bg_color_2d, self.btn_screenshot_2d
        ]:
            col_3.addWidget(btn)

        # --- COLUMN 4: SLIDERS FOR 2D VIEWER ---
        col_4 = QVBoxLayout()
        col_4.setAlignment(Qt.AlignTop)
        layout, self.slider_opacity_2d =    make_slider("Opacity   ", 0, 100, 100, self.set_opacity_2d)
        col_4.addLayout(layout)
        layout, self.slider_brightness_2d = make_slider("Brightness", 0, 200, 100, self.set_brightness_2d)
        col_4.addLayout(layout)
        layout, self.slider_contrast_2d =   make_slider("Contrast  ", 0, 200, 100, self.set_contrast_2d)
        col_4.addLayout(layout)
        layout, self.slider_saturation_2d = make_slider("Saturation", 0, 200, 100, self.set_saturation_2d)
        col_4.addLayout(layout)

        # Add all 4 columns to bottom layout
        bottom_controls_layout.addLayout(col_1)
        bottom_controls_layout.addLayout(col_2)
        bottom_controls_layout.addLayout(col_3)
        bottom_controls_layout.addLayout(col_4)

        self.main_layout.addLayout(bottom_controls_layout, 0)

        # Home button at the bottom
        home_layout = QHBoxLayout()
        home_layout.setAlignment(Qt.AlignCenter)
        self.btn_back_to_home = QPushButton("Home")
        self.btn_back_to_home.clicked.connect(self.go_back_to_home.emit)
        home_layout.addWidget(self.btn_back_to_home)
        self.main_layout.addLayout(home_layout)

    def receive_image_list(self, image_list):
        self.three_d_viewer_component.store_images(image_list)
        self.three_d_viewer_component.plot_images()

    def _select_folder_and_load_3d_slices(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing Slices")
        if folder_path:
            self.three_d_viewer_component.load_images(folder_path)
            self.three_d_viewer_component.plot_images()

    def _select_file_and_load_2d_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_viewer_component.set_image_from_path(file_path)

    def showEvent(self, event):
        super().showEvent(event)
        self.three_d_viewer_component.showEvent(event)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.three_d_viewer_component.hideEvent(event)

    def reset_view_3d(self): 
        self.three_d_viewer_component.reset_view()

    def invert_colors_3d(self): 
        self.three_d_viewer_component.invert_colors()

    def grayscale_3d(self): 
        self.three_d_viewer_component.grayscale()

    def set_bg_color_3d(self):
        color = QColorDialog.getColor()
        if color.isValid(): 
            self.three_d_viewer_component.set_bg_color(color)

    def screenshot_3d(self): 
        self.three_d_viewer_component.screenshot()

    def set_zspacing_3d(self, val): 
        self.three_d_viewer_component.set_zspacing(val)

    def set_opacity_3d(self, val): 
        self.three_d_viewer_component.set_opacity(val)

    def set_brightness_3d(self, val): 
        self.three_d_viewer_component.set_brightness(val)

    def set_contrast_3d(self, val): 
        self.three_d_viewer_component.set_contrast(val)

    def set_saturation_3d(self, val): 
        self.three_d_viewer_component.set_saturation(val)

    def invert_colors_2d(self): 
        self.image_viewer_component.invert_colors()

    def grayscale_2d(self): 
        self.image_viewer_component.grayscale()

    def set_bg_color_2d(self):
        color = QColorDialog.getColor()
        if color.isValid(): 
            self.image_viewer_component.set_bg_color(color)

    def screenshot_2d(self): 
        self.image_viewer_component.screenshot()

    def set_opacity_2d(self, val): 
        self.image_viewer_component.set_opacity(val)

    def set_brightness_2d(self, val): 
        self.image_viewer_component.set_brightness(val)

    def set_contrast_2d(self, val): 
        self.image_viewer_component.set_contrast(val)

    def set_saturation_2d(self, val): 
        self.image_viewer_component.set_saturation(val)
