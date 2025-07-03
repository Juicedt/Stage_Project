from enum import IntEnum
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PIL import Image, ImageEnhance
import cv2 
import numpy as np

# Define the SelectionMode enum
class SelectionMode(IntEnum):
    NONE = -1
    CUT_SLICE = 0
    SELECT_BG_REF = 1
    SELECT_FG_REF = 2
    SET_AS_BG_CORRECTION = 3
    SET_AS_FG_CORRECTION = 4

class ImageViewer(QGraphicsView):
    """
    Custom QGraphicsView to show a zoomable 2D image with drag-selection.
    Supports different selection modes, each emitting a specific signal upon completion.
    """
    # Define mode-specific signals
    cut_slice_cords = pyqtSignal()
    bg_ref_cords = pyqtSignal()
    fg_ref_cords = pyqtSignal()
    set_bg_cords = pyqtSignal()
    set_fg_cords = pyqtSignal()

    slices_ready = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.setAlignment(Qt.AlignCenter)

        self._current_pil_image = None
        self.recent_selection_cords = None # Stores (x1, y1, x2, y2) of the last completed selection
        self._current_LAB_image = None  
        self._bg_lab_mean = None
        self._fg_lab_mean = None
        self._slice_storage = []

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self._current_selection_mode = SelectionMode.NONE
        self.selecting = False
        self.start_point_selection = QPointF()
        self.current_selection_rect_item = None

        self.setCursor(Qt.ArrowCursor)

    def set_image(self, pil_image: Image.Image):
        # Convert PIL Image to QImage, then to QPixmap
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")

        self._current_pil_image = pil_image
        self.original_image = pil_image

        self.pixmap_item.setPixmap(QPixmap()) 
        self.resetTransform() # Reset view

        qimage = QImage(
            pil_image.tobytes(),
            pil_image.width,
            pil_image.height,
            pil_image.width * 4, # Bytes per line for RGBA8888
            QImage.Format_RGBA8888
        )
        pixmap = QPixmap.fromImage(qimage)

        self.pixmap_item.setPixmap(pixmap)

        self.resetTransform()
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio) # Fit to view

        self.create_LAB_image()

    def set_image_from_path(self, file_path: str):
        pil_image = Image.open(file_path).convert("RGBA")
        self.set_image(pil_image)

    def create_LAB_image(self):
        """
        Opens an image using cv2, convert to LAB and store it.
        Background removal requires LAB for speed
        """
        img_np_rgba = np.array(self._current_pil_image)
        img_np_rgb = img_np_rgba[:, :, :3]
        img_np_bgr = cv2.cvtColor(img_np_rgb, cv2.COLOR_RGB2BGR)

        self._current_LAB_image = cv2.cvtColor(img_np_bgr, cv2.COLOR_BGR2LAB)

    def set_selection_active(self, mode: SelectionMode):
        """
        Activates or deactivates the drag selection functionality with a specific mode.
        When active (mode is not NONE), the cursor changes to a cross.
        """
        self._current_selection_mode = mode
        if mode != SelectionMode.NONE:
            self.setCursor(Qt.CrossCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            self.selecting = False
            if self.current_selection_rect_item:
                self.scene.removeItem(self.current_selection_rect_item)
                self.current_selection_rect_item = None
            self.recent_selection_cords = None
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            if self.current_selection_rect_item:
                self.scene.removeItem(self.current_selection_rect_item)
                self.current_selection_rect_item = None

    def mousePressEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            super().mousePressEvent(event)
            return

        if self._current_selection_mode != SelectionMode.NONE and event.button() == Qt.LeftButton:
            self.selecting = True
            self.start_point_selection = self.mapToScene(event.pos()) 

            if not self.current_selection_rect_item:
                self.current_selection_rect_item = QGraphicsRectItem(self.start_point_selection.x(),
                                                                     self.start_point_selection.y(),
                                                                     0, 0)
                self.scene.addItem(self.current_selection_rect_item)
                self.current_selection_rect_item.setPen(QPen(QColor(0, 0, 255, 180), 2, Qt.SolidLine)) # Blue, semi-transparent
            else:
                self.current_selection_rect_item.setRect(self.start_point_selection.x(),
                                                         self.start_point_selection.y(),
                                                         0, 0)
            self.current_selection_rect_item.setVisible(True)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            super().mouseMoveEvent(event)
            return

        if self.selecting:
            current_pos_scene = self.mapToScene(event.pos())
            rect = QRectF(self.start_point_selection, current_pos_scene).normalized()
            self.current_selection_rect_item.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            super().mouseReleaseEvent(event)
            return

        if self.selecting and event.button() == Qt.LeftButton:
            self.selecting = False
            end_point_selection = self.mapToScene(event.pos()) 

            rect_in_scene = QRectF(self.start_point_selection, end_point_selection).normalized()

            image_rect_in_scene = self.pixmap_item.mapRectToScene(self.pixmap_item.boundingRect())
            final_rect_clamped = rect_in_scene.intersected(image_rect_in_scene)

            x1 = int(final_rect_clamped.left())
            y1 = int(final_rect_clamped.top())
            x2 = int(final_rect_clamped.right())
            y2 = int(final_rect_clamped.bottom())

            if x1 == x2: x2 = min(x2 + 1, int(image_rect_in_scene.right()))
            if y1 == y2: y2 = min(y2 + 1, int(image_rect_in_scene.bottom()))

            self.recent_selection_cords = (x1, y1, x2, y2)

            if self._current_selection_mode == SelectionMode.CUT_SLICE:
                self.cut_slice_cords.emit()
            elif self._current_selection_mode == SelectionMode.SELECT_BG_REF:
                self.bg_ref_cords.emit()
            elif self._current_selection_mode == SelectionMode.SELECT_FG_REF:
                self.fg_ref_cords.emit()
            elif self._current_selection_mode == SelectionMode.SET_AS_BG_CORRECTION:
                self.set_bg_cords.emit()
            elif self._current_selection_mode == SelectionMode.SET_AS_FG_CORRECTION:
                self.set_fg_cords.emit()

            if self.current_selection_rect_item:
                self.current_selection_rect_item.setVisible(False)
                self.scene.removeItem(self.current_selection_rect_item)
                self.current_selection_rect_item = None
            
            self.set_selection_active(SelectionMode.NONE)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Zoom in/out with mouse wheel."""
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def return_cutout(self) -> Image.Image:
        x1, y1, x2, y2 = self.recent_selection_cords
        # Pillow's crop method takes (left, upper, right, lower)
        return self._current_pil_image.crop((x1, y1, x2, y2))

    def get_bg_lab(self): # called by signal when mouse release
        # Calculate the mean LAB values for the patch
        x1, y1, x2, y2 = self.recent_selection_cords
        patch = self._current_LAB_image[y1:y2, x1:x2]
        # Reshape to (num_pixels, 3), this is fast
        self._bg_lab_mean = np.mean(patch.reshape(-1, 3), axis=0)
        return self._bg_lab_mean


    def get_fg_lab(self): # called by signal when mouse release
        # Calculate the mean LAB values for the patch
        x1, y1, x2, y2 = self.recent_selection_cords
        patch = self._current_LAB_image[y1:y2, x1:x2]
        # Reshape to (num_pixels, 3), this is fast
        self._fg_lab_mean = np.mean(patch.reshape(-1, 3), axis=0)
        return self._fg_lab_mean

    def remove_background(self, grid_size, mask_size):
        """
        Applies background removal using squared Euclidean distance for comparison.
        Returns the processed RGBA image.
        """
        img_lab = self._current_LAB_image
        img_array = np.array(self._current_pil_image)

        height, width = img_lab.shape[:2]

        mask = np.zeros((height, width), dtype=np.uint8)


        fg_lab_ref = self._fg_lab_mean
        bg_lab_ref = self._bg_lab_mean


        for y in range(0, height, grid_size):
            for x in range(0, width, grid_size):
                tile = img_lab[y:min(y+grid_size, height), x:min(x+grid_size, width)]

                avg_lab = np.mean(tile.reshape(-1, 3), axis=0)

                # Compare squared distances to foreground/background
                diff_fg = avg_lab - fg_lab_ref
                sq_dist_fg = np.dot(diff_fg, diff_fg)

                diff_bg = avg_lab - bg_lab_ref
                sq_dist_bg = np.dot(diff_bg, diff_bg)

                if sq_dist_fg < sq_dist_bg:
                    mask[y:min(y+grid_size, height), x:min(x+grid_size, width)] = 1

        if mask_size > 0:
            kernel = np.ones((mask_size, mask_size), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        img_array[:, :, 3] = mask * 255
        final_img = Image.fromarray(img_array, 'RGBA')
        self.set_image(final_img)
        self.current_mask = mask

    def adjust_mask(self, turn_visible: bool):
        x1, y1, x2, y2 = self.recent_selection_cords

        new_mask = self.current_mask 

        if turn_visible:
            new_mask[y1:y2, x1:x2] = 1
        else:
            new_mask[y1:y2, x1:x2] = 0
        
        img_array = np.array(self._current_pil_image)
        img_array[:, :, 3] = new_mask * 255
        new_img = Image.fromarray(img_array, 'RGBA')
        self.set_image(new_img)
        self.current_mask = new_mask
               
    def store_slice(self, image):
        self._slice_storage.append(image)
        self.show_stored_slices()

    def show_stored_slices(self):
        # Shows the left to right with black borders
        # Calculate total width and max height
        total_width = sum(img.width for img in self._slice_storage)
        max_height = max(img.height for img in self._slice_storage)

        prept_slices = []
        for img in self._slice_storage:
            prept_slices.append(self.cut_inner_border(img))

        # Create a new blank image with the total size
        stitched = Image.new('RGBA', (total_width, max_height))

        # Paste each image at the correct x offset
        x_offset = 0
        for img in prept_slices:
            y_offset: int = int((max_height - img.height) / 2)
            stitched.paste(img, (x_offset, y_offset))
            x_offset += img.width
        
        self.set_image(stitched)


    def cut_inner_border(self, image) -> Image.Image:
        # Define the crop box: (left, top, right, bottom)
        border_thickness: int = 5
        left = border_thickness
        top = border_thickness
        right = image.width - border_thickness
        bottom = image.height - border_thickness
        cropped = image.crop((left, top, right, bottom))

        # Create a black background the size of og image
        bordered = Image.new('RGBA', (image.width, image.height), 'black')
        # Paste the cropped image onto the black background, offset by border
        bordered.paste(cropped, (border_thickness, border_thickness))

        return bordered
    
    def emit_stored_slices(self):
        self.slices_ready.emit(self._slice_storage)

    def invert_colors(self):
        arr = np.array(self._current_pil_image)
        arr[..., :3] = 255 - arr[..., :3]
        self._current_pil_image = Image.fromarray(arr)
        self.set_image(self._current_pil_image)

    def grayscale(self):
        self._current_pil_image = self._current_pil_image.convert("L").convert("RGBA")
        self._is_grayscale = True
        self.set_image(self._current_pil_image)

    def screenshot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)")
        if path:
            self._current_pil_image.save(path)

    def set_opacity(self, val):
        self.opacity = val / 100.0
        self.set_image(self._current_pil_image)

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
        img = self.original_image.copy()
        img = ImageEnhance.Brightness(img).enhance(getattr(self, 'brightness', 1.0))
        img = ImageEnhance.Contrast(img).enhance(getattr(self, 'contrast', 1.0))
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Color(rgb).enhance(getattr(self, 'saturation', 1.0))
        filtered = Image.merge("RGBA", (*rgb.split(), a))
        self._current_pil_image = filtered
        self._is_grayscale = False
        self.set_image(filtered)