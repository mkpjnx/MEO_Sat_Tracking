import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
while True:
    ser.flushInput()
    ser.readline().decode("ascii")
    line = ser.readline().decode("ascii").replace('\r', '').replace('\n', '')
    if len(line) > 1:
         print(line)
