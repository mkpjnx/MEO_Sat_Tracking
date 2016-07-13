"""Module to retrieve accelerometer data for parsing and enjoyment."""

import serial
import time


class Accelerometer:
    """Accelerometer class."""

ser = serial.Serial('COM3', 9600)
while True:
    #time.sleep(1)
    print(ser.readline())
    # ser.reset_input_buffer()
    #info = str(ser.readline())[2:-5].split(',')
