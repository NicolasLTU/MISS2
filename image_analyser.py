'''
Update the feed on KHO's website with the latest stacked image, complete with a spectral and spatial plot. Nicolas Martinez (UNIS/LTU) 2024

'''

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec # Used to have multiple plots in the same image
from scipy import signal
import os
import time
import re
from datetime import datetime, timezone

# Function to read PNG file
def read_png(filename):
    # Open the PNG image
    with Image.open(filename) as img:
        # Convert the image to a numpy array
        image_data = np.array(img)
    return image_data

# Function to resize the processed image to a square 400x400 image
def resize_image(image):
    # Convert NumPy array to PIL image
    pil_image = Image.fromarray(image.astype(np.uint8))

    # Resize the image to 400x400
    resized_image = pil_image.resize((400, 400), Image.Resampling.LANCZOS)
    resized_image = np.array(resized_image)
    return resized_image

# Function to process the raw image
def process_image(raw_image):
    # Apply median filter
    processed_image = signal.medfilt2d(raw_image.astype('float32'))

    # Calculate background
    bg = np.average(processed_image[0:30, 0:30])

    # Subtract background
    processed_image = np.maximum(0, processed_image - bg)

    return processed_image

# Normalise the light intensity
def normalise(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

# Fetch the path to the latest image
def get_latest_image_path(base_folder):
    # Today's date in UTC in YYYY/MM/DD format
    today_path = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    full_path = os.path.join(base_folder, today_path)
    if os.path.exists(full_path):
        # Define a regex pattern that matches the file naming convention
        pattern = r'MISS2-\d{8}-\d{6}\.png'
        all_files = [f for f in os.listdir(full_path) if re.match(pattern, f)]
        if all_files:
            # Sort files by name, latest date and time comes last
            all_files.sort()
            latest_file = all_files[-1] #last of all files
            return os.path.join(full_path, latest_file) #return full path to latest file
    return None

try:
    # Define the base path where the stacked image date directory is located
    base_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG'

    # Define the feed path where the processed spectrogram is updated (website)
    feed_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Website_Data_Feed'

    while True:
        # Get the latest image file
        latest_image_file = get_latest_image_path(base_folder)
        
        if latest_image_file:
            # Read the PNG file
            image_data = read_png(latest_image_file)

            # Process and resize the image
            processed_image = process_image(image_data)
            resized_image = resize_image(processed_image)

            start_wavelength = 395  # Start wavelength
            end_wavelength = 730    # End wavelength
            num_wavelengths = resized_image.shape[1]  # Number of columns in processed_image
            wavelengths_full = np.linspace(395, 730, num_wavelengths)

            # Configure plot layout: 1 main plot (spectrogram) and 2 subplots (spectral and spatial plots)
            image_title = os.path.basename(latest_image_file)
            fig = plt.figure(figsize=(8, 8))  # Width, height in inches
            fig.suptitle(image_title, fontsize=14)
            gs = plt.GridSpec(3, 2, width_ratios=[5, 1], height_ratios=[1, 4, 1])   # 3 rows, 3 columns grid

            # Spectrogram
            ax_main = fig.add_subplot(gs[1, 0])
            ax_main.imshow(np.sqrt(resized_image), cmap='gray', aspect='auto')
            ax_main.set_xlabel("Wavelength (nm)")
            ax_main.set_ylabel("Pixel row number")
            # Setting wavelength range on x-axis with 5 ticks
            ax_main.set_xticks(np.linspace(0, 399, 5))
            ax_main.set_xticklabels(np.linspace(390, 730, 5).astype(int))

            # Spectral plot (normalised intensity over wavelength)
            ax_spectral = fig.add_subplot(gs[0, 0])
            wavelengths = np.linspace(start_wavelength, end_wavelength, len(resized_image[0]))
            spectral_data = np.mean(resized_image, axis=0)  # Averaging data across the vertical axis
            normalised_spectral_data = normalise(spectral_data)
            ax_spectral.plot(wavelengths, normalised_spectral_data)
            ax_spectral.set_yticks(np.linspace(0, 1, 3))
            ax_spectral.set_title("Spectral Analysis")       

            # Spatial plot (normalised intensity over pixel row number)
            ax_spatial = fig.add_subplot(gs[1, 1])
            spatial_data = np.mean(resized_image, axis=1)
            normalised_spatial_data = normalise(spatial_data)
            ax_spatial.plot(normalised_spatial_data, range(resized_image.shape[0]))  # Correct axis alignment
            ax_spatial.set_xticks((np.linspace(0, 1, 3)))
            ax_spatial.set_title("Spatial Analysis")
            ax_spatial.invert_yaxis()  # Inverting the y-axis to align spatial plot direction with the main image
            plt.setp(ax_spectral.get_xticklabels(), visible=True)
            plt.setp(ax_spectral.get_yticklabels(), visible=True)

            # Tight layout to ensure no overlap
            plt.tight_layout()


            # Save the plot directly to a file
            processed_image_path = os.path.join(feed_folder, os.path.basename(latest_image_file)) #Set corresponding wavelength values (to be determined)
            plt.savefig(processed_image_path, format='png', bbox_inches='tight')

            print("Processed image saved successfully: ", processed_image_path)
        else:
            print("No new images found in today's date directory.")

        # Wait for one minute before processing the next image
        time.sleep(30)

except Exception as e:
    print(f"An error occurred: {e}")
