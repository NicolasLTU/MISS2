'''
This program uses the RGB image-columns generated every minute using the spectrograms captured by MISS2 to update a daily keogram. Nicolas Martinez (UNIS/LTU) 2024

'''

import os
import numpy as np
from PIL import Image
from datetime import datetime, timezone, timedelta
import time
import matplotlib.pyplot as plt

# Base directory where the RGB-columns are saved (yyyy/mm/dd)
rgb_dir_base = r'C:\Users\auroras\.venvMISS2\MISS2\RGB_columns'

# Directory where the keogram are placed (yyyy/mm/dd)
output_dir = r'C:\Users\auroras\.venvMISS2\MISS2\Keograms'

# Define dimensions of the keogram
num_pixels_y = 300  # Number of pixels along the y-axis
num_minutes = 24 * 60  # Total number of minutes in a day
num_pixels_x = num_minutes  # Number of pixels along the x-axis

# Initialize an empty keogram with white pixels
keogram = np.full((num_pixels_y, num_pixels_x, 3), 255, dtype=np.uint8)  # White RGB empty keogram

# Routine check of the each image's integrity. Raise an exception if the image is corrupted
def verify_image_integrity(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify the integrity of the image
        return True
    except Exception as e:
        print(f"Corrupted RGB-column image detected: {file_path} - {e}")
        return False

def add_rgb_columns(keogram, base_dir, last_processed_minute):
    # Get the current date/hour (UT) in yyyy/mm/dd format
    current_date = datetime.now(timezone.utc).strftime("%Y/%m/%d")

    # Construct the directory path for the current date
    today_RGB_dir = os.path.join(base_dir, current_date.replace('/', '\\'))

    # Get the current UTC time
    now_UT = datetime.now(timezone.utc)
    # Convert the current time to minutes since midnight (UT)
    current_minute_of_the_day = now_UT.hour * 60 + now_UT.minute

    # Initialize a set of all minutes in the day to track found minutes
    found_minutes = set()

    # Check if the daily directory exists, if not, return the original keogram (no updates)
    if not os.path.exists(today_RGB_dir):
        print(f"No directory found for today's date ({today_RGB_dir}). Skipping update.")
        return keogram

    # Iteration only over new minutes since the last processed one
    for minute in range(last_processed_minute + 1, current_minute_of_the_day):
        # Construct the filename for the RGB column image
        timestamp = now_UT.replace(hour=minute // 60, minute=minute % 60, second=0, microsecond=0)
        filename = f"MISS2-{timestamp.strftime('%Y%m%d-%H%M%S')}.png"
        file_path = os.path.join(today_RGB_dir, filename)

        # Load RGB column data if file exists AND check integrity of each image
        if os.path.exists(file_path) and verify_image_integrity(file_path):
            try:
                rgb_data = np.array(Image.open(file_path))
                # Ensure the RGB data has the correct shape (300, 1, 3)
                if rgb_data.shape == (num_pixels_y, 1, 3):
                    keogram[:, minute:minute+1, :] = rgb_data  # Add RGB column to keogram
                    found_minutes.add(minute)
                else:
                    print(f"Skipped {filename} due to incorrect shape: {rgb_data.shape}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Fill in missing minutes with black images
    missing_minutes = set(range(last_processed_minute + 1, current_minute_of_the_day)) - found_minutes
    for minute in missing_minutes:
        keogram[:, minute:minute+1, :] = 0  # Black RGB column

    return keogram

# Ensure that any pre-existing keogram for today will be loaded and updated
def load_existing_keogram(output_dir):
    # Get the current UTC time
    current_utc_time = datetime.now(timezone.utc)
    
    # If the current time is before 00:05, load the keogram from the previous day
    if current_utc_time.hour == 0 and current_utc_time.minute < 5:
        previous_date = (current_utc_time - timedelta(days=1)).strftime('%Y/%m/%d')
        keogram_path = os.path.join(output_dir, previous_date.replace('/', '\\'), 'keogram-MISS2.png')
        if os.path.exists(keogram_path):
            # Load the existing keogram if it exists
            with Image.open(keogram_path) as img:
                keogram = np.array(img)
                last_processed_minute = 1439  # Last minute of the day
            return keogram, last_processed_minute
        else:
            # Otherwise, initialize a new keogram
            return np.full((300, 1440, 3), 255, dtype=np.uint8), 0  # White RGB empty keogram and last processed minute as 0
    
    # Otherwise, load the keogram for the current day
    else:
        # Get the current UTC date
        current_date = current_utc_time.strftime('%Y/%m/%d')
        keogram_path = os.path.join(output_dir, current_date.replace('/', '\\'), 'keogram-MISS2.png')
        if os.path.exists(keogram_path):
            # Load the existing keogram if it exists
            with Image.open(keogram_path) as img:
                keogram = np.array(img)
                last_processed_minute = 1439  # Last minute of the day
            return keogram, last_processed_minute
        else:
            # Otherwise, initialize a new keogram
            return np.full((300, 1440, 3), 255, dtype=np.uint8), 0  # White RGB empty keogram and last processed minute as 0

def save_keogram(keogram, output_dir):
    # Get the current UTC time
    current_utc_time = datetime.now(timezone.utc)
    # Create the directory path for the current date
    current_date_dir = os.path.join(output_dir, current_utc_time.strftime('%Y/%m/%d'))
    os.makedirs(current_date_dir, exist_ok=True)

    # Plot and save the keogram
    fig, ax = plt.subplots(figsize=(20, 6))
    ax.imshow(keogram, aspect='auto', extent=[0, 24*60, 90, -90])
    ax.set_title(f"Meridian Imaging Svalbard Spectrograph II (KHO/UNIS) {current_utc_time.strftime('%Y-%m-%d')}", fontsize=20)

    # Set x-axis for hours
    x_ticks = np.arange(0, 24*60, 60)  # Positions for each hour
    x_labels = [f"{hour}:00" for hour in range(24)]  # Labels for each hour
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Time (UT)")

    #Set y-axis for south, zenith and north
    y_ticks = np.linspace(-90, 90, num=7)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(['South', '60° S', '30° S', 'Zenith', '30° N', '60° N', '90° N'])
    ax.set_ylim(-90, 90)
    ax.set_ylabel("Zenith angle (degrees)")

    # Save the updated keogram
    keogram_filename = os.path.join(current_date_dir, f'keogram-MISS2-{current_utc_time.strftime("%Y%m%d")}.png')
    plt.savefig(keogram_filename)
    plt.close(fig)
    print(f"Keogram saved: {keogram_filename}")

# Update the keogram every 5 minutes
def main():
    while True:  # Start of the infinite loop
        try:
            # Get the current UTC time
            current_utc_time = datetime.now(timezone.utc) 

            # Check if it's time for an update (every 5 minutes)
            if current_utc_time.minute % 5 == 0:
                # Continue updating the existing keogram
                keogram, last_processed_minute = load_existing_keogram(output_dir)  # Unpack the returned values correctly

                # Update the keogram
                keogram = add_rgb_columns(keogram, rgb_dir_base, last_processed_minute)
                save_keogram(keogram, output_dir)
                print("Update completed.")
            else:
                print("Waiting for the next update...")

            # Wait for 1 minute before the next check
            time.sleep(60)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

