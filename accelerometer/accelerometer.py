"""Module to retrieve accelerometer data for parsing and enjoyment."""

import serial
# import time


class Accelerometer:
    """Accelerometer class."""

    def __init__(self, port, baud=9600):
        """Initialize with the serial port and the baudrate."""
        self.ser = serial.Serial(port, baud)
        self.ser.reset_input_buffer()
        self.info = str(self.ser.readline())[2:-5].split(',')

    def refresh(self):
        """Read a line from the accelerometer and update the info."""
        self.info = str(self.ser.readline())[2:-5].split(',')
        self.x, self.y, self.z, self.xa, self.ya, self.za, self.o = self.info
