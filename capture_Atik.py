'''
This program controls all the Atik414EX functions and the way the raw scaled PNG 16-bit unsigned images are saved. Nicolas Martinez (UNIS/LTU) 

'''

import os
import numpy as np
import datetime
from PIL import Image, PngImagePlugin
import AtikSDK
import time

camera = AtikSDK.AtikSDKCamera() 
exposure_duration = 12  # Exposure time per image, in seconds
optimal_temperature = 2 # Optimal Temperature for cooling
imaging_cadence = 15 # Capture images every X seconds
camera.connect()

def monitor_temperature(camera):
    optimal_temperature = 2  # Target temperature, about 20 degrees below ambient temperature with +/- 2 degree margin

    try:
        current_temperature = camera.get_temperature()
        print("Current temperature:", current_temperature)

        if current_temperature > optimal_temperature:
            camera.set_cooling(True)  # Activate cooling
        elif current_temperature < optimal_temperature:
            camera.set_cooling(False)  # Deactivate cooling

    except Exception as e:
        print(f"Error in temperature monitoring: {e}")
        time.sleep(60)  # Sleep for 60 seconds before retrying


def capture_images(temp_folder, camera):

    try:
        while True:
            current_time = datetime.datetime.now(datetime.timezone.utc)
            
            # Check time to capture images only at fixed time instants
            if (current_time.second % imaging_cadence != 0):
                time.sleep(0.5) # Sleep a bit before checking time again
                continue
                
            # Capture an image with the specified exposure time
            image_array = camera.take_image(exposure_duration)
            uint16_array = image_array.astype(np.uint16)

            # Retrieve the current temperature
            try:
                current_temperature = camera.get_temperature()
                print("Current temperature:", current_temperature)

                if current_temperature > optimal_temperature:
                    camera.set_cooling(True)  # Activate cooling
                elif current_temperature < optimal_temperature:
                    camera.set_cooling(False)  # Deactivate cooling

            except Exception as e:
                print(f"Could not retrieve temperature: {e}")
                current_temperature = "Unknown"

            # Save the image with metadata
            timestamp = current_time.strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(temp_folder, f"MISS2-{timestamp}.png")

            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("Exposure Time", str(exposure_duration) + " seconds")
            metadata.add_text("Date/Time", timestamp)
            metadata.add_text("Temperature", f"{current_temperature} C")
            metadata.add_text("Note", "MISS2 KHO/UNIS")

            img = Image.fromarray(uint16_array)
            img.save(image_path, "PNG", pnginfo=metadata)

            print(f"Saved image: {image_path}")

    except Exception as e:
        print(f"Error during image capture and save: {e}")
    finally:
        try:
            camera.disconnect()
        except:
            pass



PNG_folder = r"C:\Users\auroras\.venvMISS2\MISS2\Captured_PNG\Temporary_RAW"

try:
    capture_images(PNG_folder, camera)
except KeyboardInterrupt:
    print("Image capture stopped manually (ctrl+c). Please hold...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    camera.disconnect()
