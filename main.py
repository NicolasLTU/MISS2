'''
This main program commands the entire MISS2-Software. Nicolas Martinez (UNIS/LTU) 2024

'''

import signal
import subprocess
import time
import serial
from datetime import datetime

from solar_zenith_calculator import it_is_daytime #Program used to check if it's daytime at KHO (Kjell Henriksen Observatory), returns a Boolean
from sunshield_controller import SunShield_CLOSE, SunShield_OPEN, init_serial #Control of the SunShield shutter: Close, Open, Settings for communication to the Serial Port 'COM3'

#from fakezenith import it_is_daytime2 #Test the Atik responsiveness during switch from night to day time.
#import AtikSDK

def stop_processes(processes, timeout=5):
    for process in processes:
        process.terminate()  # Ask the process to terminate
        try:
            process.wait(timeout=timeout)  # Wait for the process to terminate
        except subprocess.TimeoutExpired:
            print(f"Process {process.pid} did not terminate in time. Forcing termination.")
            process.kill()  # Forcefully terminate the process

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
    #start_time = datetime.now()
try:
    ser = init_serial()
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    ser = None


    # Start keogram_maker and RGB_column_maker
    keogram_process = subprocess.Popen(["python", r"C:\Users\auroras\.venvMISS2\MISS2\MISS2_Software\keogram_maker.py"])
    processes.append(keogram_process)
    rgb_column_process = subprocess.Popen(["python", r"C:\Users\auroras\.venvMISS2\MISS2\MISS2_Software\RGB_column_maker.py"])
    processes.append(rgb_column_process)
    average_png_process = subprocess.Popen(["python", r"C:\Users\auroras\.venvMISS2\MISS2\MISS2_Software\average_PNG_maker.py"])
    processes.append(average_png_process)
    image_analyser_process = subprocess.Popen(["python", r"C:\Users\auroras\.venvMISS2\MISS2\MISS2_Software\image_analyser.py"])
    processes.append(image_analyser_process)
    image_capture_process = None  # Track the Atik_controller.py process

    try:
        while running:
            if it_is_daytime():  # If it's daytime, stop processes 
                print ('Daytime: MISS2 is OFF')
                if image_capture_process:
                    print("Terminating image capture process...")
                    stop_processes([image_capture_process])
                    processes.remove(image_capture_process)
                    image_capture_process = None  # Reset the variable
                if ser:
                    SunShield_CLOSE(ser) #Close the SunShield
            else:  # Nighttime
                print ('Nighttime: MISS2 is Operational')
                if not image_capture_process:  # If Atik_controller.py isn't running
                    if ser:
                        SunShield_OPEN(ser) #Open the SunShield
                    print("Starting Atik_controller.py...")
                    image_capture_process = subprocess.Popen(["python", "C:\\Users\\auroras\\.venvMISS2\\MISS2\\MISS2_Software\\capture_Atik.py"])
                    processes.append(image_capture_process)          
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("Interrupt received, cleaning up...")
    finally:
        stop_processes(processes)
        if camera:
            camera.disconnect()
