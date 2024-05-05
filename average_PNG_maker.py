'''
Takes care of the raw images saved by the Atik 414EX in a temporary folder (to limit the amount of tasks performed by the programn operating the Atik 414EX). 
It averages them minute-wise, saves an average image in a special date directory and then moves all averaged raw images in their respective date directory. Nicolas Martinez UNIS/LTU 2024

'''



import os
import datetime
import time
import numpy as np
from PIL import Image
import re
from collections import defaultdict

def average_images(temp_folder, PNG_folder, raw_PNG_folder, current_time):
    images_by_minute = defaultdict(list)
    filename_regex = re.compile(r'^.+-(\d{8})-(\d{6})\.png$')

    # Convert current time to UTC
    current_time_utc = current_time.astimezone(datetime.timezone.utc)

    # Group images based on the minute they belong to
    for filename in os.listdir(temp_folder):
        filepath = os.path.join(temp_folder, filename)
        match = filename_regex.match(filename)
        if match:
            date_part, time_part = match.groups()
            image_utc = datetime.datetime.strptime(date_part + time_part[:4], "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc)
            prev_minute = current_time_utc - datetime.timedelta(minutes=1)
            if image_utc < prev_minute:
                images_by_minute[date_part + '-' + time_part[:4]].append(filepath)

    # Process each group of images
    for minute_key, filepaths in images_by_minute.items():
        year, month, day, hour, minute = map(int, [minute_key[:4], minute_key[4:6], minute_key[6:8], minute_key[9:11], minute_key[11:]])
        target_utc = datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)

        # Check if the current time is at least 30 seconds past the next minute
        if target_utc < current_time_utc - datetime.timedelta(minutes=1) and current_time_utc.second >= 30:

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
                    date_part = os.path.basename(filepath).split('-')[1][:8]
                    image_datetime = datetime.datetime.strptime(date_part, "%Y%m%d")
                    raw_save_folder = os.path.join(raw_PNG_folder, f"{image_datetime.year:04d}", f"{image_datetime.month:02d}", f"{image_datetime.day:02d}")
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
        current_time = datetime.datetime.now()
        average_images(temp_folder, PNG_folder, raw_PNG_folder, current_time)
        time.sleep(30 - (current_time.second % 30))  # Sleep until 30 seconds past the minute
    except Exception as e:
        print(f"An error occurred: {e}")
