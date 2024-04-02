'''
This main program commands the entire MISS2-Software. Nicolas Martinez (UNIS/LTU) 2024

'''

import signal
import subprocess
import time

import solar_zenith_calculator #Program used to check if it's daytime at KHO (Kjell Henriksen Observatory), returns Boolean
from sunshield_controller import SunShield_CLOSE, SunShield_OPEN, init_serial #Control of the SunShield shutter: Close, Open, Settings for communication to the Serial Port 'COM3'


#import AtikSDK

def stop_processes(processes):
    for process in processes:
        process.terminate()
        process.wait()

def signal_handler(sig, frame):
    global running
    stop_processes(processes)
    if camera:
        camera.disconnect()
    running = False
    print("Stopped the program.")
    exit(0)

processes = []
camera = None
running = True  # To manage the while loop

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # Start keogram_maker and RGB_column_maker
    keogram_process = subprocess.Popen(["python", "C:\\Users\\auroras\\.venvMISS2\\MISS2\\MISS2_Software\\keogram_maker.py"])
    processes.append(keogram_process)
    rgb_column_process = subprocess.Popen(["python", "C:\\Users\\auroras\\.venvMISS2\\MISS2\\MISS2_Software\\RGB_column_maker.py"])
    processes.append(rgb_column_process)

    image_capture_process = None  # Track the Atik_controller.py process
    ser = init_serial() #Fetch the required settings for sending instruction to the SunShield shutter

    try:
        while running:
            if solar_zenith_calculator.is_it_daytime():  # If it's daytime, then 
                if image_capture_process:
                    print("Terminating image capture process...")
                    stop_processes([image_capture_process])
                    processes.remove(image_capture_process)
                    image_capture_process = None  # Reset the variable
                SunShield_CLOSE(ser) #Close the SunShield
            else:  # Nighttime
                if not image_capture_process:  # If Atik_controller.py isn't running
                    SunShield_OPEN(ser) #Open the SunShield
                    print("Starting Atik_controller.py...")
                    image_capture_process = subprocess.Popen(["python", "C:\\Users\\auroras\\.venvMISS2\\MISS2\\MISS2_Software\\Atik_controller.py"])
                    processes.append(image_capture_process)
            time.sleep(300)  # Check every 5 minutes
    except KeyboardInterrupt:
        print("Interrupt received, cleaning up...")
    finally:
        stop_processes(processes)
        if camera:
            camera.disconnect()
