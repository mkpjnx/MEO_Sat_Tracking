import serial
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
while True:
    line = ser.readline().decode('ascii')
    print(str(line))
