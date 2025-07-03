from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class HomeScreenWidget(QWidget):
    """
    The home screen widget for the Brain Slice Application.
    Two large buttons to go to the 3D Viewer or the Slice Preparer.
    Emits signals when a button is clicked.
    """

    goto_3d_viewer = pyqtSignal()
    goto_slice_preparer = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):

        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addStretch()

        title_label = QLabel("Brain Slice Application")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_label.setFont(title_font)

        layout.addWidget(title_label)

        layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Horizontal layout for buttons
        button_row_layout = QHBoxLayout()
        button_row_layout.addStretch()

        button_font = QFont()
        button_font.setPointSize(16)
        button_font.setBold(True)

        # Button for 3D Viewer
        btn_3d_viewer = QPushButton("3D Viewer")
        btn_3d_viewer.setFont(button_font)
        btn_3d_viewer.setFixedSize(200, 70)
        btn_3d_viewer.clicked.connect(self.goto_3d_viewer.emit)
        button_row_layout.addWidget(btn_3d_viewer)

        button_row_layout.addSpacerItem(QSpacerItem(50, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Button for Slice Preparer
        btn_slice_preparer = QPushButton("Slice Preparer")
        btn_slice_preparer.setFont(button_font)
        btn_slice_preparer.setFixedSize(200, 70)
        btn_slice_preparer.clicked.connect(self.goto_slice_preparer.emit)
        button_row_layout.addWidget(btn_slice_preparer)

        button_row_layout.addStretch()

        layout.addLayout(button_row_layout)
        layout.addStretch()

