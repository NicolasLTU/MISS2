'''
Process raw image to update feed on KHO's website with latest image every minute. Nicolas Martinez (UNIS/LTU) 2024

'''

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os
import time

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
    resized_image = pil_image.resize((400, 400))

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

try:
    # Define the path to the raw_temp folder - test folder used here:
    temp_folder = r'C:\Users\auroras\.venvMISS2\Test_Imager\raw_temp'

    # Get the path to the latestfilenames.txt file
    filename_txt = os.path.join(temp_folder, "latest_filenames.txt")

    while True:
        # Check if the file exists
        if os.path.exists(filename_txt):
            # Read the file and extract the latest filename
            with open(filename_txt, "r") as file:
                filenames = file.readlines()

            # Get the latest filename (the last one in the list)
            if filenames:
                latest_filename = filenames[-1].strip()
                filename = os.path.join(temp_folder, latest_filename)

                # Read the PNG file
                image_data = read_png(filename)

                # Process and resize the image
                processed_image = process_image(image_data)
                resized_image = resize_image(processed_image)

                # Plotting
                plt.imshow(np.sqrt(resized_image), cmap='gray', aspect='equal')
                plt.xlabel("Wavelength (nm)")
                plt.ylabel("Pixel row number")
                
                pixel_positions = [10, 110, 210, 310] #adapt to actual pixel-wavelength equivalence
                wavelengths = [400,500,600,700]
                plt.xticks(pixel_positions, wavelengths)
                plt.title(latest_filename)
                # Save the plot directly to a file
                processed_image_path = os.path.join(r"C:\Users\auroras\.venvMISS2\Test_Imager\WebsiteFeedSimulation", latest_filename)
                plt.savefig(processed_image_path, format='png', bbox_inches='tight')

                print("Processed image saved successfully.")

            else:
                print("No filenames found in latestfilenames.txt.")
        else:
            print("latestfilenames.txt not found.")

        # Wait for one minute before processing the next image
        time.sleep(60)

except Exception as e:
    print(f"An error occurred: {e}")
