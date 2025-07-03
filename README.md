# 3D - Brain Slice Viewer and Microscopy Slide Processor

A Python based prototype of a desktop application for the processing of microscopy slides of brain slices into stacked 3D-Models that allow interactive malipulation for visualisation purposes. This tool allows for quick partially automated proccesing of microscopy slides, converting image files, cutting up images, background removal, and projection in 3D in a time efficient manner.


---

## Table of Contents

- Key Features
- Core Workflows
- Installation
- Usage
- VSI to PNG Converter prototype*
- Project Structure diagram


## Key Features

-   **Interactive 2D Image Viewers**: Pan, zoom, and inspect images.
-   **Slice Cropping**: Manually cut out slices from source images.
-   **Semi-Automated Background Removal**: Uses LAB color space for more acurate color detection.
-   **Slice Management**: Store processed slices for preview.
-   **Interactive 3D Visualization**: Full Control of 3D-object orientation.
-   **Image Adjustments**: Apply filters for brightness, contrast, saturation, convertion to grayscale and invertion of colors in both the 2D and 3D views.
-   **Standalone Script**: A prototype script to convert .vsi files to the standard .png format required by the application.

## Workflows

### 1. Slice Preparation

The processing of png images is handled on the **Slice Preparer** screen.

1.  **Load Image**: Click "Select Image" to load the png of the microscopy slide containing brain slices.
2.  **Select References**: Use "Select Fg" and "Select Bg" to drag-select area's of the foreground and background. This tells the algorithm what sections should be removed when removing the background.
3.  **Cut Slice**: Click "Cut Slice". Drag-select a slice you want to process. It will appear in the middle viewer after selection.
4.  **Remove Background**: Adjust the "Grid Size" and "Mask Size" parameters if needed. Click "Rm Bg". The background of the cropped slice will be made transparent.
5.  **Correct Mask**: Use "Set as Fg" or "Set as Bg" to manually correct possible mistakes made by the algorithm.
6.  **Store Slice**: Click "Store Slice". The processed slice appears on the right in the preview viewer.
7.  **Repeat**: Repeat steps 3-6 for all slices in the source image.
8.  **Finalize**: Click "Send to 3D Viewer" to transfer the cut slices to the 3D viewer.

### 2. 3D Visualization

Inspecting the the 3D visualisation of the slices is handled on the **3D Viewer** screen.

1.  **Receive Slices**: Slices sent from the Slice Preparer will automatically load and render.
2.  **Load from Folder**: Use "Select Folder" to load a folder containing processed pngs of slices.
3.  **Manipulate View**: Use the buttons and sliders to adjust the 3D model.
4.  **2D Inspection**: Use "Select Image" to load any image for closer inspection.

## Installation

The application requires the installation of the following packages: 
- PyQt5
- numpy
- Pillow
- opencv-python
- pyvista
- pyvistaqt


To install, first clone the repository and set up a virtual environment. Then install the listed requirements.




## Usage

### Running the Application

You can run the main application from the root directory of the project: python Main.py

### The Main Screens

-   **Home Screen**: The initial landing page. From here, you can navigate to either the Slice Preparer or the 3D Viewer.
-   **Slice Preparer**: The page for image processing.
-   **3D Viewer**: The page for 3D model visualization.

## VSI to PNG Converter


**IMPORTANT:** This script is a prototype and has hardcoded file paths. You must edit the script before running it. This script also requires a JDK. OpenJDK was used, but was cause for repeated errors. These errors were not fully worked out time of at publishing.



## Project Structure

```
.
├── Main.py                   # Main application 
├── home_screen.py            # Home screen.
├── slice_preparer.py         # Slice preparation.
├── three_d_viewer_widget.py  # 3D viewer screen.
├── image_viewer.py           # 2D viewer.
├── three_d_viewer.py         # 3D renderer.
├── VSItoPNG.py               # Converting .vsi to .png.
└── README.md                 # This file.
```


