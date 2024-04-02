'''
This program uses the RGB image-columns generated every minute using the spectrograms captured by MISS2 to update a daily keogram. Nicolas Martinez (UNIS/LTU) 2024

'''

import os
import numpy as np
from PIL import Image
from datetime import datetime, timezone
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

def add_rgb_columns(keogram, base_dir):
    
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
    for minute in range(current_minute_of_the_day):
        # Construct the filename for the RGB column image
        timestamp = now_UT.replace(hour=minute // 60, minute=minute % 60, second=0, microsecond=0)
        filename = f"MISS2-{timestamp.strftime('%Y%m%d-%H%M%S')}.png"
        file_path = os.path.join(today_RGB_dir, filename)

        # Load RGB column data if file exists AND check ibtegrity of each image
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
    missing_minutes = set(range(current_minute_of_the_day)) - found_minutes
    for minute in missing_minutes:
        keogram[:, minute:minute+1, :] = 0  # Black RGB column

    return keogram

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
            # Reinitialize the keogram for each update cycle
            keogram = np.full((num_pixels_y, num_pixels_x, 3), 255, dtype=np.uint8)  # White RGB empty keogram
            updated_keogram = add_rgb_columns(keogram, rgb_dir_base)
            save_keogram(updated_keogram, output_dir)
            print("Update completed. Waiting 5 minutes for the next update...")
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(300) #Update the keogram every 5 minutes

if __name__ == "__main__":
    main()