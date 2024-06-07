'''
This program controls all the Atik414EX functions and the way the raw scaled PNG 16-bit unsigned images are saved. Nicolas Martinez (UNIS/LTU) 

''' #Last update 11.05.2024 - implementation of binning options and init of the camera left

import os
import numpy as np
import datetime
from PIL import Image, PngImagePlugin
import AtikSDK
import time



#print (dir(AtikSDK.AtikSDKCamera()))

# Path to the yyy/mm/dd date directory where all new captured images will be saved.
raw_PNG_folder = os.path.join(os.path.expanduser("~"), ".venvMISS2/MISS2/Captured_PNG/raw_PNG")


camera = AtikSDK.AtikSDKCamera() 
exposure_duration = 0.05  # Exposure time per image, in seconds
optimal_temperature = 0 # Optimal Temperature for cooling
imaging_cadence = 5 # Capture images every X second

# Horizontal and vertical binning of the images captured and saved
binX = 2
binY = 2 

# Camera connection and initialisation
camera.connect()
if camera.is_connected():
    print ("Connected device:", camera.get_device_name(0))
else:
    print("Failed to connect to the camera.")

# Exposure settings
camera.set_exposure_speed(exposure_duration)

# Set binning
camera.set_binning(binX, binY)

camera.set_cooling(optimal_temperature)

# Gain control
#camera.set_gain_offset(100)

# Dark mode for dark frame substraction
#camera.set_dark_mode(enable=True)

def capture_and_save_images(base_folder, camera ):

    try:
        while True:
            current_time = datetime.datetime.now(datetime.timezone.utc)
            
            # Check time to capture images only at fixed time instants
            if (current_time.second % imaging_cadence != 0):
                time.sleep(0.5) # Sleep a bit before checking time again
                continue

            date_folder = os.path.join(base_folder, current_time.strftime("%Y/%m/%d"))
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)

            # Capture an image with the specified exposure time
            image_array = camera.take_image(exposure_duration)
            uint16_array = image_array.astype(np.uint16)

            # Flip the image vertically if it is saved upside down
            uint16_array = np.flipud(uint16_array)

            # Retrieve the current temperature
            try:
                current_temperature = camera.get_temperature()
                print("Current temperature:", current_temperature)
            except Exception as e:
                print(f"Could not retrieve temperature: {e}")
                current_temperature = "Unknown"       

            # Save the image with metadata
            timestamp = current_time.strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(date_folder, f"MISS2-{timestamp}.png")

            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("Exposure Time", str(exposure_duration) + " seconds")
            metadata.add_text("Date/Time", timestamp)
            metadata.add_text("Temperature", f"{current_temperature} C")
            metadata.add_text("Note", "MISS2 KHO/UNIS")
            metadata.add_text("Binning", f"{binX}x{binY}")

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

try:
    capture_and_save_images(raw_PNG_folder, camera)
except KeyboardInterrupt:
    print("Image capture stopped manually (ctrl+c). Please hold...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    camera.disconnect()









'''
    dir(AtikSDK)

Camera Connection and Information:

connect
disconnect
is_connected
is_device_present
is_local_connection
device_count
device_in_use
device_has_filterwheel
device_has_guideport
get_device_name
get_device_serial
get_api_version
get_dll_version
get_firmware_versions
get_serial

Camera State and Control:

camera_state
camera_connection_state
cooler_warmup
cooling_info
set_cooling
set_cooling_power
can_control_shutter
can_set_shutter_speed
close_shutter
open_shutter
pulse_guide
guide
guide_port
set_dark_mode
get_dark_mode
continuous_mode_supported
set_continuous_mode
start_fast_mode
start_fast_exposure
start_overlapped_exposure
stop_exposure
stop_guiding
stop_guiding_before_download
shutter_speed
set_shutter_speed
exposure_time_remaining
set_triggered_exposure

Image Acquisition and Handling:

take_image
take_image_ms
get_image_data
download_percent
last_exposure_duration
get_last_exposure_start_time

Exposure Control:

set_exposure_speed
get_exposure_speed

Filter Wheel Control (EFW):

connect_efw
disconnect_efw
is_efw_connected
is_efw_present
efw_device_details
efw_num_positons
get_current_efw_positon
set_efw_position
move_internal_filterwheel
internal_filterwheel_info

Other Features:

initialise_lens
set_lens_aperture
get_lens_aperture
set_lens_focus
get_lens_focus
set_pad_data
get_pad_data
set_processing
get_processing
set_subframe
get_subframe
set_subframe_position
set_subframe_sample
set_subframe_size
set_window_heater_power
get_window_heater_power
precharge_mode
overlapped_exposure_valid
shutdown
refresh_device_count
set_fast_callback
set_gain_offset
get_gain_offset
get_gain_offset_range
set_16bit_mode
get_16bit_mode
has_16bit_mode
set_binning
get_binning
set_preview
set_column_repair_columns
clear_column_repair_columns
set_column_repair_fix_columns
get_columns_repair_columns
get_column_repair_can_fix_columns
get_column_repair_fix_columns
set_amplifier
get_amplifier
start_overlapped_exposure
set_overlapped_exposure_time
set_pad_data
'''