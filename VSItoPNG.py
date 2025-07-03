import os
import glob
import javabridge # python_javabridge fork - NOT original javabridge
import bioformats
import numpy as np
from PIL import Image

""" PROTOTYPE HARDCODED TO SPECIFICK ENVIROMENT """



def process_vsi_file(vsi_path, series_index, user_series_number, output_dir):
    filename = os.path.splitext(os.path.basename(vsi_path))[0]

    rdr = bioformats.formatreader.make_image_reader_class()()
    rdr.setId(vsi_path)
    rdr.setSeries(series_index)

    width = rdr.getSizeX()
    height = rdr.getSizeY()
    channels = rdr.getSizeC()

    # Read image data for z=0, c=0, t=0
    index = rdr.getIndex(0, 0, 0)
    pixel_bytes = rdr.openBytes(index)
    img_array = np.frombuffer(pixel_bytes, dtype=np.uint8)
    img_array = img_array.reshape((height, width, channels))

    pil_img = Image.fromarray(img_array)

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{filename}_S{user_series_number}.png"
    pil_img.save(os.path.join(output_dir, output_filename))

    rdr.close()
    print(f"Saved: {output_filename}")

def main():
    vsi_folder = "E:\Slidescanner 02-05-2025"
    save_root = "E:\SlidescannerPNGs"

    user_series_number = 17  # ← Set this to match what you see in Fiji (1-based)
    series_index = user_series_number - 1  # Bio-Formats uses 0-based indexing

    javabridge.start_vm(class_path=bioformats.JARS)
    try:
        vsi_files = glob.glob(os.path.join(vsi_folder, "*.vsi"))
        for vsi_path in vsi_files:
            output_subfolder = f"Series_{user_series_number}_PNGs"
            output_dir = os.path.join(save_root, output_subfolder)
            process_vsi_file(vsi_path, series_index, user_series_number, output_dir)
    finally:
        javabridge.kill_vm()

if __name__ == "__main__":
    main()
