import os
import numpy as np
from PIL import Image, ImageEnhance
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog

import pyvista as pv
from pyvistaqt import QtInteractor


class ThreeDViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plotter = QtInteractor(self)
        self.layout.addWidget(self.plotter.interactor)

        self.plotter.add_axes()
        self.plotter.view_xy()
        self.plotter.set_background("gray")

        self.images = []               # currently displayed images
        self.original_images = []     # original images
        self.meshes = []

        self.opacity = 1.0
        self.zspacing = 5.0

        self.brightness = 1.0
        self.contrast = 1.0
        self.saturation = 1.0
        self.is_grayscale = False

    def load_images(self, folder_path: str):
        """Loads all PNG images from folder, resets state, and plots."""
        image_files = sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".png")
        ])
        self.original_images = [
            Image.open(img).convert("RGBA") for img in image_files
        ]
        self.images = list(self.original_images)
        self.is_grayscale = False
        self.plot_images()

    def store_images(self, images):
        self.original_images = list(images)
        self.images = list(images)
        self.is_grayscale = False

    def plot_images(self):
        self.plotter.clear()
        self.meshes = []

        for i, img in enumerate(self.images):
            img_array = np.array(img)
            texture = pv.Texture(img_array)
            h, w = img_array.shape[:2]
            plane = pv.Plane(i_size=w, j_size=h)
            plane = plane.translate((0, 0, -i * self.zspacing))
            mesh = self.plotter.add_mesh(plane, texture=texture, opacity=self.opacity, name=f"slice_{i}")
            self.meshes.append(mesh)

        self.plotter.reset_camera()
        self.plotter.render()

    def showEvent(self, event):
        super().showEvent(event)
        self.plotter.show()
        self.plotter.render()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.plotter.hide()

    def reset_view(self):
        self.plotter.view_xy()
        self.plotter.reset_camera()
        self.plotter.render()

    def invert_colors(self):
        new_images = []
        for img in self.images:
            arr = np.array(img)
            arr[..., :3] = 255 - arr[..., :3]
            new_images.append(Image.fromarray(arr))
        self.images = new_images
        self.plot_images()

    def grayscale(self):
        if not self.is_grayscale:
            self.images = [img.convert("L").convert("RGBA") for img in self.images]
            self.is_grayscale = True
        else:
            self.images = list(self.original_images)
            self.is_grayscale = False
        self.plot_images()

    def set_bg_color(self, color):
        self.plotter.set_background(color.name())
        self.plotter.render()

    def screenshot(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)"
        )
        if path:
            self.plotter.screenshot(path)

    def set_opacity(self, val):
        self.opacity = val / 100.0
        self.plot_images()

    def set_zspacing(self, val):
        self.zspacing = val / 10.0
        self.plot_images()

    def set_brightness(self, val):
        self.brightness = val / 100.0
        self._apply_filters()

    def set_contrast(self, val):
        self.contrast = val / 100.0
        self._apply_filters()

    def set_saturation(self, val):
        self.saturation = val / 100.0
        self._apply_filters()

    def _apply_filters(self):
        """Applies all filters: brightness, contrast, saturation to original images."""
        new_images = []
        for img in self.original_images:
            filtered = ImageEnhance.Brightness(img).enhance(self.brightness)
            filtered = ImageEnhance.Contrast(filtered).enhance(self.contrast)
            r, g, b, a = filtered.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageEnhance.Color(rgb).enhance(self.saturation)
            filtered = Image.merge("RGBA", (*rgb.split(), a))
            new_images.append(filtered)
        self.images = new_images
        self.is_grayscale = False
        self.plot_images()
