'''
Averages the raw PNG captured by the Atik 414EX detector minute-wise and saves all averaged raw images in their respective date directory. Nicolas Martinez UNIS/LTU 2024

'''

import os
import datetime
import time
import numpy as np
from PIL import Image
import re
from collections import defaultdict

def average_images(PNG_folder, raw_PNG_folder, current_time, processed_minutes):
    images_by_minute = defaultdict(list)
    filename_regex = re.compile(r'^.+-(\d{8})-(\d{6})\.png$') #regex 

    # Convert current time to UTC
    current_time_utc = current_time.astimezone(datetime.timezone.utc)

    # Group images based on the minute they belong to
    for root, dirs, files in os.walk(raw_PNG_folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            match = filename_regex.match(filename)
            if match:
                date_part, time_part = match.groups()
                image_date = datetime.datetime.strptime(date_part, "%Y%m%d").replace(tzinfo=datetime.timezone.utc).date()
                current_date = current_time_utc.date()
                if image_date == current_date:
                    image_utc = datetime.datetime.strptime(date_part + time_part[:4], "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc)
                    prev_minute = current_time_utc - datetime.timedelta(minutes=1)
                    if image_utc < prev_minute:
                        images_by_minute[date_part + '-' + time_part[:4]].append(filepath)

    # Process each minute-group of images IF not already processed
    for minute_key, filepaths in images_by_minute.items():
        if minute_key not in processed_minutes:  # Check if the minute has already been processed
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

                    # Update the list of already processed minutes to the list
                    processed_minutes.append(minute_key)

raw_PNG_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\raw_PNG'
PNG_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\averaged_PNG'

# List to keep track of processed minutes 
processed_minutes = []

while True:
    try:
        current_time = datetime.datetime.now()
        average_images(PNG_folder, raw_PNG_folder, current_time, processed_minutes)
        time.sleep(30 - (current_time.second % 30))  # Sleep until 30 seconds past the minute
    except Exception as e:
        print(f"An error occurred: {e}")
