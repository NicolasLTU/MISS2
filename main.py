'''
This main program commands the entire MISS2-Software. Nicolas Martinez (UNIS/LTU) 2024

'''

import signal
import subprocess
import time
import serial
from datetime import datetime

from astronomical_twilight_calculator import it_is_nighttime #Program used to check if the Sun is below -10 degrees of elevation at KHO (Kjell Henriksen Observatory), returns a Boolean
from sunshield_controller import SunShield_CLOSE, SunShield_OPEN, init_serial #Control of the SunShield shutter: Close, Open, Settings for communication to the Serial Port 'COM3'


processes = []
camera = None
running = True  # To manage the while loop
image_capture_process = None
is_currently_night = None 


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

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    #start_time = datetime.now()
try:
    ser = init_serial()
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    ser = None


    # Start keogram_maker and RGB_column_maker
    keogram_process = subprocess.Popen(["python", "C:/Users/auroras/.venvMISS2/MISS2/MISS2_Software/keogram_maker.py"])
    processes.append(keogram_process)
    rgb_column_process = subprocess.Popen(["python", "C:/Users/auroras/.venvMISS2/MISS2/MISS2_Software/RGB_column_maker.py"])
    processes.append(rgb_column_process)
    average_png_process = subprocess.Popen(["python", "C:/Users/auroras/.venvMISS2/MISS2/MISS2_Software/average_PNG_maker.py"])
    processes.append(average_png_process)
    image_analyser_process = subprocess.Popen(["python", "C:/Users/auroras/.venvMISS2/MISS2/MISS2_Software/image_analyser.py"])
    processes.append(image_analyser_process)
    image_capture_process = None  # Track the Atik_controller.py process

    try:
        while running:
            if it_is_nighttime():
                if is_currently_night is not True: # Check for transition day-night
                    is_currently_night = True
                    print ('Daytime: MISS2 is Operational')
                if ser:
                    SunShield_CLOSE(ser) #Close the SunShield
                if not image_capture_process:
                    image_capture_process = subprocess.Popen(["python", r"C:\Users\auroras\.venvMISS2\MISS2\MISS2_Software\capture_Atik.py"])
                    processes.append(image_capture_process)

            else:  # Daytime
                if is_currently_night is not False: # Check for transition night-day
                    is_currently_night = False
                    print ("Daytime: MISS 2 is OFF")
                    if image_capture_process:
                        print("Stopping image capture...")
                        stop_processes([image_capture_process])
                        processes.remove(image_capture_process)
                        image_capture_process = None
                    if ser:
                        SunShield_CLOSE(ser) # Close the SunShield
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("Interrupt received, cleaning up...")
    finally:
        stop_processes(processes)
        if camera:
            camera.disconnect()
