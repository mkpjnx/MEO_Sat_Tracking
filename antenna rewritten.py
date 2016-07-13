import time
import ephem
import serial

#Constants

initial_az = 180
initial_alt = 90
min_elevation = 10.0
sleep_time = 15.0
unwind_threshold = 180
sleep_on_unwind = 45.0

class SerialTester:
    def write(self,line):
        print(line)

    def read(self, num):
        return

class Antenna:
    azimuth = initial_az
    altitude = initial_alt
    parked = True

    def set_position(self, az, alt):
        self.azimuth = az
        self.altitude = alt
        az_int = round(az)
        alt_int = round(alt)
        ser.write(":Sz " + str(az_int) + "*00:00#")
        ser.write(":Sa +" + str(alt_int) + "*00:00#")
        ser.write(":MS#")
        ser.read(64)

    def park(self):
        if (self.parked):
            print('Antenna Parked')
        else:
            print('Parking Antenna')
            self.set_position(initial_az, initial_alt)
            self.parked = True

    def move(self, az, alt):
        if (self.parked):
            self.parked = False
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
        
def set_home():
    home = ephem.Observer()
    #Set LAT/LON Coordinates to IMSA's location
    home.lon = '-88.787'
    home.lat = '41.355'
    #Set elevation in meters
    home.elevation = 200
    return home    

def setup_serial():
    # Set Serial Port - USB0
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) 
    print('Current Port Used is ' + ser.name) 
    return ser
#    return SerialTester()

def setup_satellite():
    # Read in TLE for target satellite ICO F2
    icof2 = ephem.readtle('ICO F2',
               '1 26857U 01026A   16172.60175106 -.00000043  00000-0  00000+0 0  9997',
               '2 26857 044.9783   5.1953 0013193 227.2968 127.4685 03.92441898218058') 
    return icof2

def to_degrees(radians):
    return radians * 180.0 / ephem.pi

def get_sat_position(icof2, home):
    icof2.compute(home)
    icof2_az = to_degrees(icof2.az)
    icof2_alt = to_degrees(icof2.alt)
    print('Current Satellite Location: Azimuth %3.2f deg, Altitude %3.2f deg' % (icof2_az, icof2_alt))
    return icof2_az, icof2_alt

home = set_home()
ser = setup_serial()
icof2 = setup_satellite()
antenna = Antenna()
               
while True:
    home.date = ephem.now()
#    home.date = "2016-06-28 12:00:00"
    icof2_az, icof2_alt = get_sat_position(icof2, home)

        # Operate the antenna if the satellite's elevation is greater than 10
        # degrees
        # If the elevation IS above 10 degrees and the antenna is parked, then
        # unlatch the park_latch variable
    if (icof2_alt >= min_elevation):
        antenna.move(icof2_az, icof2_alt)       
    else:
        antenna.park()
            
    time.sleep(sleep_time)