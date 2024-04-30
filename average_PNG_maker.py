import os
import datetime
import time
import numpy as np
from PIL import Image
import re
from collections import defaultdict

def average_images(temp_folder, PNG_folder, raw_PNG_folder, images_per_minute=6): # Based on how many images are saved per minute
    images_by_minute = defaultdict(list)
    filename_regex = re.compile(r'^.+-(\d{8})-(\d{6})\.png$')

    # Group images by their timestamp (up to the minute)
    for filename in os.listdir(temp_folder):
        filepath = os.path.join(temp_folder, filename)
        match = filename_regex.match(filename)
        if match:
            date_part, time_part = match.groups()
            minute_key = date_part + '-' + time_part[:4]  # YYYYMMDD-HHMM for grouping
            images_by_minute[minute_key].append(filepath)

    # Process each group of images only if they form a complete set of X images per minute
    for minute_key, filepaths in images_by_minute.items():
        if len(filepaths) == images_per_minute:  # Check for a complete set
            sum_img_array = None
            count = 0
        for filepath in filepaths:
            try:
                img = Image.open(filepath)
                img_array = np.array(img)

                if sum_img_array is None:
                    sum_img_array = np.zeros_like(img_array, dtype='float64')

                sum_img_array += img_array
                count += 1

                # Move the original raw image to the specified directory
                year, month, day, hour, minute = map(int, [minute_key[:4], minute_key[4:6], minute_key[6:8], minute_key[9:11], minute_key[11:]])
                raw_save_folder = os.path.join(raw_PNG_folder, f"{year:04d}", f"{month:02d}", f"{day:02d}")
                os.makedirs(raw_save_folder, exist_ok=True)
                raw_image_path = os.path.join(raw_save_folder, os.path.basename(filepath))
                os.rename(filepath, raw_image_path)
            except Exception as e:
                print(f"Error processing image {os.path.basename(filepath)}: {e}")

        # If images were found for this minute, average them and save
        if count > 0:
            averaged_image = (sum_img_array / count).astype(np.uint16)
            save_folder = os.path.join(PNG_folder, f"{year:04d}", f"{month:02d}", f"{day:02d}")
            os.makedirs(save_folder, exist_ok=True)
            averaged_image_path = os.path.join(save_folder, f"MISS2-{year:04d}{month:02d}{day:02d}-{hour:02d}{minute:02d}00.png")

            # Convert numpy array back to an Image object and specify the mode for 16-bit
            averaged_img = Image.fromarray(averaged_image, mode='I;16')
            averaged_img.save(averaged_image_path)
            print(f"Saved averaged image: {averaged_image_path}")

temp_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\Temporary_RAW'
PNG_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG'
raw_PNG_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\raw_PNG'

while True:
    try:
        average_images(temp_folder, PNG_folder, raw_PNG_folder)
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(60)  # Wait for 60 seconds before the next iteration
