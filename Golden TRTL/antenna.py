import time
import serial
import sys


#Constants
initial_az = 180
initial_alt = 90
min_elevation = 10.0
sleep_time = 1.0
unwind_threshold = 180
sleep_on_unwind = 45.0

class SerialTester:
    def write(self,line):
        print(line)

    def read(self, num):
        return

class Antenna:


    def __init__(self, port, baud):
        '''Initialize with the unparsed sentence'''
        self.azimuth = initial_az
        self.altitude = initial_alt
        self.parked = True
        self.ser = Serial(port, baud)

    def set_position(self, az, alt):
        self.azimuth = az
        self.altitude = alt
        az_int = round(az)
        alt_int = round(alt)
        self.ser.write(":Sz " + str(az_int) + "*00:00#")
        self.ser.write(":Sa +" + str(alt_int) + "*00:00#")
        self.ser.write(":MS#")
        self.ser.read(64)

    def park(self):
        if (self.parked):
            print('Antenna Parked')
        else:
            print('Parking Antenna')
            self.set_position(initial_az, initial_alt)
            self.parked = True

    def move(self, az, alt):
        if (az >= min_elevation):
                    # Unwrap Cable if Azimuth will cross through True North
                    # In the above case, Set Azimuth to 180 Degrees, then pick up
                    # normal tracking
                    # Then sleep 45 seconds to give the positioner time to
                    # reposition
            if ((self.azimuth - az) > unwind_threshold):
                self.set_position(initial_az, self.altitude)
                print('Repositioning to unwrap cable')
                time.sleep(sleep_on_unwind)
            else:
                print('Tracking Mode')
                self.set_position(az, alt)
        else:
            antenna.park()
