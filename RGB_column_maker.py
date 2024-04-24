""" 
This program is designed to constantly look for new PNG files in the RGB_columns directory and produce (300,1,3) PGN-files (8-bit unsigned integer) out of them. Nicolas Martinez (UNIS/LTU) 2024

"""

import datetime as dt
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from PIL import Image
import time
from datetime import datetime, timezone, timedelta

#spectro_path = r'C:\Users\auroras\.venvMISS2\Test_Imager\raw_temp' # Directory of the PNG (16-bit) images taken by MISS2

spectro_path = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG' # Directory of the PNG (16-bit) images taken by MISS2
output_folder_base = r'C:\Users\auroras\.venvMISS2\MISS2\RGB_columns' # Directory where the 8-bit RGB-columns are saved

#Column where the centre of brightest emission line (to be identified experimentally)
column_428 = 248
column_558 = 511
column_630 = 666


#Columns marking the north and south lines of horizon respectively (to be determined experimentally)
north_col = 267
south_col = 70

processed_images = set()  # To keep track of processed images


# Ensure directory exist before trying to open it or save RGB
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
# Routine check of the each image's integrity. Raise an exception if the image is corrupted
def verify_image_integrity(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify() 
        with Image.open(file_path) as img:
            img.load()  
        return True 
    except Exception as e:
        print(f"Corrupted raw PNG detected: {file_path} - {e}")
        return False

#Read the PNG-images (spectrograms)
def read_png(filename):
    # Open the PNG image
    with Image.open(filename) as img:
        # Convert the image to a numpy array
        raw_data = np.array(img)
    return raw_data

#Subtract background from the RGB images
def process_image(raw_image):
    # Apply median filter
    processed_image = signal.medfilt2d(raw_image.astype('float32'))
    # Calculate background
    bg = np.average(processed_image[0:30, 0:30])
    # Subtract background
    processed_image = np.maximum(0, processed_image - bg)
    return processed_image

# From the spectrogram, extract, process and average each emission line
def process_emission_line(spectro_path, emission_column):
    spectro_png = Image.open(spectro_path)
    spectro_array = np.array(spectro_png)

    start_column = max(emission_column - 1 , 0)
    end_column = min(emission_column +1, spectro_array.shape[1])

    extracted_columns = spectro_array[south_col:north_col, start_column:end_column]

    #Process the extracted columns
    processed_columns = process_image(extracted_columns)

    #Average the processed columns to obtain a (1,height) 
    averaged_column = np.mean(processed_columns, axis=1)
    # Flatten the columns to one dimension
    flattened_column = averaged_column.flatten()

    return flattened_column, flattened_column.shape

# Take processed emission lines to create a RGB
def PNG_to_RGB (spectro_data, column_630, column_558, column_428):

    #Use processed averaged columns for the making of the RGB-column
    column_RED, shape_RED = process_emission_line(spectro_data, column_630)
    column_GREEN, shape_GREEN = process_emission_line(spectro_data, column_558)
    column_BLUE, shape_BLUE = process_emission_line(spectro_data, column_428)

    #print("Shape of RED column:", shape_RED)
    #print("Shape of GREEN column:", shape_GREEN)
    #print("Shape of BLUE column:", shape_BLUE)


    # Reshape the columns to have a single channel
    column_RED = column_RED.reshape(-1, 1)
    column_GREEN = column_GREEN.reshape(-1, 1)
    column_BLUE = column_BLUE.reshape(-1, 1)

    RGB_image= np.dstack((column_RED, column_GREEN, column_BLUE))
    #print("Shape of RGB-column:", RGB_image.shape)

    return RGB_image

def create_rgb_columns():
    current_time_UT = datetime.now(timezone.utc)
    input_folder = os.path.join(spectro_path, current_time_UT.strftime("%Y/%m/%d"))
    output_folder = os.path.join(output_folder_base, current_time_UT.strftime("%Y/%m/%d"))
    ensure_directory_exists(input_folder)
    ensure_directory_exists(output_folder)

    matching_files = [f for f in os.listdir(input_folder) if f.startswith("MISS2-") and f.endswith(".png") and f <= current_time_UT.strftime("MISS2-%Y%m%d-%H%M%S.png")]


    for filename in matching_files:
        if filename in processed_images:
            continue

        png_file_path = os.path.join(input_folder, filename)

        # Check each image's integrity. Skip processing if the image is corrupted.
        if not verify_image_integrity(png_file_path):
            print(f"Skipping corrupted image: {filename}")
            continue  # Skip this iteration and move to the next file

        #spectro_data = read_png(png_file_path)
        RGB_image = PNG_to_RGB(png_file_path, column_630, column_558, column_428)
        RGB_pil_image = Image.fromarray(RGB_image.astype('uint8'))
        resized_RGB_image = RGB_pil_image.resize((1, 300), Image.Resampling.LANCZOS)

        base_filename = filename[:-4]  # Remove the '.png' extension
        output_filename = f"{base_filename[:-2]}00.png"  # Replace seconds with '00' and add back the '.png' extension
        output_filename_path = os.path.join(output_folder, output_filename)


        resized_RGB_image.save(output_filename_path)
        print(f"Saved RGB column image: {output_filename}")

        # Add the processed image to the set of processed images
        processed_images.add(filename)

while True:
    create_rgb_columns()
    
    time.sleep(60)
