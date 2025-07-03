import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

# Import the individual screen widgets
from home_screen import HomeScreenWidget
from three_d_viewer_widget import ThreeDViewerWidget
from slice_preparer import SlicePreparerWidget

class MyApp(QMainWindow):
    """
    The main application window that manages the screens (Home, 3D Viewer, Slice Preparer).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brain Slice Application")
        self.show() 

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create instances of each screen widget
        self.home_screen = HomeScreenWidget()
        self.three_d_viewer = ThreeDViewerWidget()
        self.slice_preparer = SlicePreparerWidget()

        # Add each screen to the stacked widget.
        # The order here determines their index 
        self.stacked_widget.addWidget(self.home_screen)      # Index 0 for Home Screen
        self.stacked_widget.addWidget(self.three_d_viewer)   # Index 1 for 3D Viewer
        self.stacked_widget.addWidget(self.slice_preparer)   # Index 2 for Slice Preparer

        # Connect signals from the screen widgets to slots in MyApp for navigation
        # When a button on the home screen is clicked, it emits a signal.
        self.home_screen.goto_3d_viewer.connect(self.show_3d_viewer)
        self.home_screen.goto_slice_preparer.connect(self.show_slice_preparer)

        # Connect signals from the viewer/preparer screens to go back to home
        self.three_d_viewer.go_back_to_home.connect(self.show_home_screen)
        self.slice_preparer.go_back_to_home.connect(self.show_home_screen)

        self.slice_preparer.viewer_final_output.slices_ready.connect(self.three_d_viewer.receive_image_list)
        # Set the initial screen to the home screen
        self.show_home_screen()


    def show_home_screen(self):
        """Switches to the home screen."""
        self.stacked_widget.setCurrentIndex(0) # Index 0 self.home_screen

    def show_3d_viewer(self):
        """Switches to the 3D viewer screen."""
        self.stacked_widget.setCurrentIndex(1) # Index 1 self.three_d_viewer

    def show_slice_preparer(self):
        """Switches to the slice preparer screen."""
        self.stacked_widget.setCurrentIndex(2) # Index 2 self.slice_preparer

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())

