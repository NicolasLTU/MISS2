""" 
This program is designed to constantly look for new PNG files in the RGB_columns directory and produce (300,1,3) PGN-files (8-bit unsigned integer) out of them. Nicolas Martinez (UNIS/LTU) 2024
"""

import datetime as dt
import os
import numpy as np
from PIL import Image
from scipy import signal
import time
from datetime import datetime, timezone

spectro_path = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\averaged_PNG' # Directory of the PNG (16-bit) images taken by MISS2
output_folder_base = r'C:\Users\auroras\.venvMISS2\MISS2\RGB_columns' # Directory where the 8-bit RGB-columns are saved

# Row where the centre of brightest lines of auroral emission are to be found (to be identified experimentally)
row_428 = 1027 # based on blue channel analysis of the light refracted by the dispersive element of MISS 2 
row_558 = 687 # based on green channel analysis of the light refracted by the dispersive element of MISS 2 
row_630 = 381 # based on red channel analysis of the light refracted by the dispersive element of MISS 2 

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

# Read the PNG-images (spectrograms)
def read_png(filename):
    # Open the PNG image
    with Image.open(filename) as img:
        # Convert the image to a numpy array
        raw_data = np.array(img)
    return raw_data

# Subtract background from the RGB images
def process_image(raw_image):
    # Apply median filter
    processed_image = signal.medfilt2d(raw_image.astype('float32'))
    # Calculate background
    bg = np.average(processed_image[0:30, 0:30])
    # Subtract background
    processed_image = np.maximum(0, processed_image - bg)
    return processed_image

# From the spectrogram, extract, process and average each emission line
def process_emission_line(spectro_path, emission_row):
    spectro_png = Image.open(spectro_path)
    spectro_array = np.array(spectro_png)

    start_row = max(emission_row - 1 , 0)
    end_row = min(emission_row +1, spectro_array.shape[0])

    extracted_rows = spectro_array[start_row:end_row, :]

    # Process the extracted rows
    processed_rows = process_image(extracted_rows)

    # Average the processed rows to obtain a (length, 1) 
    averaged_row = np.mean(processed_rows, axis=0)
    # Flatten the rows to one dimension
    flattened_row = averaged_row.flatten()

    return flattened_row, flattened_row.shape

# Take processed emission lines to create a RGB
def PNG_to_RGB (spectro_data, row_630, row_558, row_428):

    #Use processed averaged rows for the making of the RGB-column
    column_RED, shape_RED = process_emission_line(spectro_data, row_630)
    column_GREEN, shape_GREEN = process_emission_line(spectro_data, row_558)
    column_BLUE, shape_BLUE = process_emission_line(spectro_data, row_428)

    #print("Shape of RED column:", shape_RED)
    #print("Shape of GREEN column:", shape_GREEN)
    #print("Shape of BLUE column:", shape_BLUE)

    # Increase the red channel by multiplying it with a factor
    red_factor = 1.0  # Adjust this factor as needed
    column_RED *= red_factor

    # Increase the green channel by multiplying it with a factor
    green_factor = 1.0  # Adjust this factor as needed
    column_GREEN *= green_factor

    # Increase the blue channel by multiplying it with a factor
    blue_factor = 1.0  # Adjust this factor as needed
    column_BLUE *= blue_factor

    # Reshape the columns to have a single channel
    column_RED = column_RED.reshape(-1, 1)
    column_GREEN = column_GREEN.reshape(-1, 1)
    column_BLUE = column_BLUE.reshape(-1, 1)

    RGB_image= np.dstack((column_RED, column_GREEN, column_BLUE))
    #print("Shape of RGB-column:", RGB_image.shape)

    return RGB_image

def get_user_input_date():
    while True:
        try:
            user_date_str = input("Enter the date (yyyy/mm/dd): ")
            user_date = dt.datetime.strptime(user_date_str, "%Y/%m/%d")
            return user_date
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy/mm/dd format.")

def create_rgb_columns():
    global processed_images # Make the variable global

    user_date = get_user_input_date()
    
    current_day = user_date.day

    input_folder = os.path.join(spectro_path, user_date.strftime("%Y/%m/%d"))
    output_folder = os.path.join(output_folder_base, user_date.strftime("%Y/%m/%d"))
    ensure_directory_exists(input_folder)
    ensure_directory_exists(output_folder)

    matching_files = [f for f in os.listdir(input_folder) if f.startswith("MISS2-") and f.endswith(".png")]

    for filename in matching_files:
        if filename in processed_images:
            continue

        png_file_path = os.path.join(input_folder, filename)

        # Check each image's integrity. Skip processing if the image is corrupted.
        if not verify_image_integrity(png_file_path):
            print(f"Skipping corrupted image: {filename}")
            continue  # Skip this iteration and move to the next file

        RGB_image = PNG_to_RGB(png_file_path, row_630, row_558, row_428)
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
    
    time.sleep(60) # One update per minute
