import time
import ephem
#import serial
import io
import sys
import string

from datetime import datetime

initial_az = int(180)
initial_alt = int(90)
mount_az = int(initial_az)
park_latch = True    # Sets initial state to Parked

class SerialTester:
    def write(self,line):
        print(line)

    def read(self, num):
        return

# Set Serial Port - USB0
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser = SerialTester()
#print("Current Port Used is " + ser.name)

#Updates time and location later
def update(obs):
    obs.date = ephem.now()
    obs.date = "2016-06-28 12:00:00"
    obs.lon = '-88.787'
    obs.lat = '41.355'
    obs.elevation = 200

#Returns the az/alt of the body as a tuple from the perspective of the obs
def get_az_alt(obs, body):
    body.compute(home)
    az = body.az
    alt = body.alt
    return (az/ephem.degree, alt/ephem.degree)

#Rotates and returns azimuth of mount
def rotate(mount_az, current_az, current_alt):
    # Unwrap Cable if Azimuth will cross through True North
    # In the above case, Set Azimuth to 180 Degrees, then pick up normal tracking
    # Then sleep 45 seconds to give the positioner time to reposition
    if ((mount_az - current_az) > 270):
            ser.write(":Sz " + str(initial_az) + "*00:00#")
            ser.write(":MS#")
            ser.read(64)
            print('Repositioning to unwrap cable')
            time.sleep(45.0)
            return initial_az
    else:
            print ('Tracking Mode')
            ser.write(":Sz " + str(current_az) + "*00:00#")
            ser.write(":Sa +" + str(current_alt) + "*00:00#")
            ser.write(":MS#")
            ser.read(64)
            return current_az


home = ephem.Observer()
satellite = ephem.readtle('ICO F2',
               '1 26857U 01026A   16172.60175106 -.00000043  00000-0  00000+0 0  9997',
               '2 26857 044.9783   5.1953 0013193 227.2968 127.4685 03.92441898218058')

while True:
    update(home)
    satellite_az_deg, satellite_alt_deg = get_az_alt(home, satellite)
    print('Current Satellite Location: Azimuth %3.2f deg, Altitude %3.2f deg' % (satellite_az_deg, satellite_alt_deg))

    # Operate the antenna if the satellite's elevation is greater than 10 degrees
    # If the elevation IS above 10 degrees and the antenna is parked, then unlatch the park_latch variable
    if satellite_alt_deg <= 10:
        mount_az = rotate(mount_az, round(initial_az), round(initial_alt))
        print('Antenna Parked' if park_latch else "Parking Antenna")
        park_latch = True
    else:
        mount_az = rotate(mount_az, round(satellite_az_deg), round(satellite_alt_deg))
        park_latch = False

    time.sleep(1.0)
