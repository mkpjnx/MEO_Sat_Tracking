import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
while True:
    ser.flushInput()
    ser.readline()
    try:
        line = ser.readline().decode("ascii").replace('\r', '').replace('\n', '')
    except:
        line = ""
    if len(line) > 1:
         print(line.split(','))
