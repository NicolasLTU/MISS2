'''
This program controls all the Atik414EX functions and the way the raw scaled PNG 16-bit unsigned images are saved. Each saved image is the result of the averaging of 4 pictures taken every minute. Nicolas Martinez (UNIS/LTU) 

'''


import os
import sys
import time
import datetime
import numpy as np
from PIL import Image
from PIL import PngImagePlugin
import AtikSDK


def monitor_temperature(camera):
    optimal_temperature = 2  # Target temperature, about 20 degrees below ambient temperature

    try:
        current_temperature = camera.get_temperature()
        print("Current temperature:", current_temperature)

        if current_temperature > optimal_temperature:
            camera.set_cooling(True)  # Activate cooling
        elif current_temperature < optimal_temperature:
            camera.set_cooling(False)  # Deactivate cooling

    except Exception as e:
        print(f"Error in temperature monitoring: {e}")
        time.sleep(60)  # Sleep for 1 minute before retrying

def capture_images(PNG_folder, camera=None):
    # If camera is not provided, connect here. This is for standalone usage.
    if camera is None:
        try:
            camera = AtikSDK.AtikSDKCamera()
            camera.connect()  # Connect to the camera
            own_camera = True  # Flag to track if the script made the connection
        except Exception as e:
            print(f"Error: Could not connect to the camera: {e}")
            return
    else:
        own_camera = False  # Camera is managed externally, don't disconnect here

    print("Starting to capture images...")  # Notify when starting to capture images

    cycle_start_time = time.time()
    images = []
    exposure_duration = 12  # Set exposure time per image, in seconds

    # Retrieve the current temperature
    try:
        current_temperature = camera.get_temperature()
    except Exception as e:
        print(f"Could not retrieve temperature: {e}")
        current_temperature = "Unknown"

    for _ in range(4):  # Capture 4 images per minute
        image_array = camera.take_image(exposure_duration)

        # Scale the pixel values to the range [0, 2^16 - 1] (16-bit)
        scaled_array = (image_array / np.max(image_array)) * (2**16 - 1)
        uint16_array = scaled_array.astype(np.uint16)
        images.append(uint16_array)

    # Average the images
    averaged_image = np.mean(images, axis=0).astype(np.uint16)

    # Save the averaged image
    current_time = datetime.datetime.now(datetime.timezone.utc)
    timestamp = current_time.strftime("MISS2-%Y%m%d-%H%M%S")
    stack_folder = os.path.join(PNG_folder, current_time.strftime("%Y/%m/%d"))
    os.makedirs(stack_folder, exist_ok=True)
    averaged_image_path = os.path.join(stack_folder, f"{timestamp}.png")

    # Create metadata (with relevant data/information)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Exposure Time", str(exposure_duration) + " seconds")
    metadata.add_text("Pictures in Stack", "4")
    metadata.add_text("Date/Time", timestamp)
    metadata.add_text("Temperature", f"{current_temperature} C")
    metadata.add_text("Note", "MISS2 KHO/UNIS")

    # Save the image with metadata
    img = Image.fromarray(averaged_image)
    img.save(averaged_image_path, "PNG", pnginfo=metadata)
    
    print(f"Saved image: {averaged_image_path}")

    if own_camera:
        camera.disconnect()  # Only disconnect if this script made the connection


#Definition of the 60 second loops
if __name__ == "__main__":
    capture_folder = r'C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG'
    if "noconnect" in sys.argv:
        while True:
            start_cycle_time = time.time()
            capture_images(capture_folder)
            end_cycle_time = time.time()
            cycle_duration = end_cycle_time - start_cycle_time
            if cycle_duration < 60:
                time.sleep(60 - cycle_duration)
    else:
        camera = AtikSDK.AtikSDKCamera()
        try:
            camera.connect()
            while True:
                start_cycle_time = time.time()

                monitor_temperature(camera)  # Perform temperature check right away

                capture_images(capture_folder, camera)  # Then immediately proceed to capture images

                # Calculate the elapsed time and sleep the remainder of the 60 seconds, if any
                elapsed_time = time.time() - start_cycle_time
                if elapsed_time < 60:
                    time.sleep(60 - elapsed_time)

        finally:
            camera.disconnect()