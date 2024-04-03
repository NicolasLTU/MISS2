'''
This program controlls all the Atik414EX functions and the way the raw unsigned scaled PNG 16-bit images are saved. Each saved image is the result of the averaging of 4 pictures taken every minute. Nicolas Martinez (UNIS/LTU) 

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
    if camera is None:
        try:
            camera = AtikSDK.AtikSDKCamera()
            camera.connect()
            own_camera = True
        except Exception as e:
            print(f"Error: Could not connect to the camera: {e}")
            return
    else:
        own_camera = False

    print("Starting to capture images...")
    exposure_duration = 12  # Exposure time per image, in seconds

    try:
        current_temperature = camera.get_temperature()
    except Exception as e:
        print(f"Could not retrieve temperature: {e}")
        current_temperature = "Unknown"

    images = []
    for i in range(4):  # Adjusted to capture 4 images per minute
        image_array = camera.take_image(exposure_duration)
        scaled_array = (image_array / np.max(image_array)) * (2**16 - 1)
        uint16_array = scaled_array.astype(np.uint16)
        images.append(uint16_array)

        # Adjustments for saving raw images with metadata in 'raw_PNG' subdirectory
        raw_image_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("MISS2-%Y%m%d-%H%M%S")
        raw_folder_path = os.path.join(PNG_folder, datetime.datetime.now().strftime("%Y/%m/%d"), "raw_PNG")
        os.makedirs(raw_folder_path, exist_ok=True)
        raw_image_path = os.path.join(raw_folder_path, f"{raw_image_timestamp}-{i+1}.png")
        
        # Create and save raw images with metadata
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Exposure Time", str(exposure_duration) + " seconds")
        metadata.add_text("Date/Time", raw_image_timestamp)
        metadata.add_text("Temperature", f"{current_temperature} C")
        metadata.add_text("Note", "MISS2 KHO/UNIS")
        img = Image.fromarray(uint16_array)
        img.save(raw_image_path, "PNG", pnginfo=metadata)

    # Average the images and save the result with metadata, as before
    averaged_image = np.mean(images, axis=0).astype(np.uint16)
    current_time = datetime.datetime.now(datetime.timezone.utc)
    timestamp = current_time.strftime("MISS2-%Y%m%d-%H%M%S")
    stack_folder = os.path.join(PNG_folder, current_time.strftime("%Y/%m/%d"))
    os.makedirs(stack_folder, exist_ok=True)
    averaged_image_path = os.path.join(stack_folder, f"{timestamp}.png")

    img = Image.fromarray(averaged_image)
    img.save(averaged_image_path, "PNG", pnginfo=metadata)
    
    print(f"Saved image: {averaged_image_path}")

    if own_camera:
        camera.disconnect() 


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
