'''
This program commands the SunShield shutter to OPEN (S0\r) or CLOSE (S1\r). Nicolas Martinez (UNIS/LTU) 2024

'''

import serial
import serial.tools.list_ports

# Function to initialize and open the serial port
def init_serial():
    try:
        ser = serial.Serial(
            port='COM3',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )  # Parameters according to SunShield User Manual (Keo Scientific)
        print("Serial port initialized successfully")
        return ser
    except FileNotFoundError as e:
        print(f"Failed to open serial port: {e}")
        return None

def SunShield_CLOSE(ser):
    try:
        print("Sending CLOSE command...")
        ser.write(b'S1\r')
        response = ser.readline()
        print(f"Response to CLOSE command: {response.decode().strip()}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")

def SunShield_OPEN(ser):
    try:
        print("Sending OPEN command...")
        ser.write(b'S0\r')
        response = ser.readline()
        print(f"Response to OPEN command: {response.decode().strip()}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")

# Test functions
if __name__ == "__main__":
    ser = init_serial()  
    SunShield_OPEN(ser)     
    SunShield_CLOSE(ser)   
    ser.close()
