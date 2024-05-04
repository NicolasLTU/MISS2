import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Base directory where the RGB image-columns are saved (yyyy/mm/dd)
rgb_dir_base = r'C:\Users\auroras\.venvMISS2\MISS2\RGB_columns'

# Directory where the keograms are placed (yyyy/mm/dd)
output_dir = r'C:\Users\auroras\.venvMISS2\MISS2\Keograms'

# Define dimensions of the keogram
num_pixels_y = 300  # Number of pixels along the y-axis
num_minutes = 24 * 60  # Total number of minutes in a day
num_pixels_x = num_minutes  # Number of pixels along the x-axis

def verify_image_integrity(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify the integrity of the image
        return True
    except Exception as e:
        print(f"Corrupted RGB-column image detected: {file_path} - {e}")
        return False

def add_rgb_columns(keogram, base_dir, date):
    # Construct the directory path for the given date
    rgb_dir = os.path.join(base_dir, date.replace('/', '\\'))

    # Iterate over all minutes of the day
    for minute in range(num_minutes):
        # Construct the filename for the RGB column image
        filename = f"MISS2-{date.replace('/', '')}-{minute//60:02d}{minute%60:02d}00.png"
        file_path = os.path.join(rgb_dir, filename)

        # Check if RGB image exists for the target date and is valid
        if os.path.exists(file_path) and verify_image_integrity(file_path):
            try:
                rgb_data = np.array(Image.open(file_path))
                # Ensure the RGB data has the correct shape (300, 1, 3)
                if rgb_data.shape == (num_pixels_y, 1, 3):
                    keogram[:, minute:minute+1, :] = rgb_data  # Add RGB column to keogram
                else:
                    print(f"Skipped {filename} due to incorrect shape: {rgb_data.shape}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        else:
            print(f"No RGB data found for minute {minute} of {date}")
            # Replace missing RGB data with black pixels
            keogram[:, minute:minute+1, :] = 0

    return keogram

def save_keogram(keogram, output_dir, date):
    # Create the directory path for the given date
    date_dir = os.path.join(output_dir, date.replace('/', '\\'))
    os.makedirs(date_dir, exist_ok=True)

    # Plot and save the keogram
    fig, ax = plt.subplots(figsize=(20, 6))
    ax.imshow(keogram, aspect='auto', extent=[0, 24*60, 90, -90])
    ax.set_title(f"Meridian Imaging Svalbard Spectrograph II (KHO/UNIS) {date}", fontsize=20)

    # Set x-axis for hours
    x_ticks = np.arange(0, 24*60, 60)  # Positions for each hour
    x_labels = [f"{hour}:00" for hour in range(24)]  # Labels for each hour
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Time (UT)")

    # Set y-axis for south, zenith, and north
    y_ticks = np.linspace(-90, 90, num=7)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(['South', '60° S', '30° S', 'Zenith', '30° N', '60° N', '90° N'])
    ax.set_ylim(-90, 90)
    ax.set_ylabel("Zenith angle (degrees)")

    # Save the keogram in the date directory
    keogram_filename = os.path.join(date_dir, f'keogram-MISS2-{date.replace("/", "")}.png')
    plt.savefig(keogram_filename)
    plt.close(fig)
    print(f"Keogram saved: {keogram_filename}")

def main():
    # Input the date for which you want to generate the keogram
    target_date = input("Enter the date (yyyy/mm/dd) for the keogram: ")

    # Initialize an empty keogram with white pixels
    keogram = np.full((num_pixels_y, num_pixels_x, 3), 255, dtype=np.uint8)

    # Add RGB columns to the keogram
    keogram = add_rgb_columns(keogram, rgb_dir_base, target_date)

    # Save the keogram
    save_keogram(keogram, output_dir, target_date)

if __name__ == "__main__":
    main()