import time
import ephem
import serial
import nmea
import orientation
import sys
import threading
from geomag import geomag

#Constants
initial_az = 180
initial_alt = 90
min_elevation = 10.0
sleep_time = 1.0
unwind_threshold = 180
sleep_on_unwind = 45.0

last_lon = '-88.787'
last_lat = '41.355'
last_heading = 0.0

mount_port = '/dev/ttyUSB0'
arduino_port = '/dev/ttyACM0'

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

def reset():
    obs = ephem.Observer()
    #Set LAT/LON Coordinates to IMSA's location
    obs.date = ephem.now()
    obs.lon = last_lon
    obs.lat = last_lat
    obs.elevation = 0.0
    return obs

def update_gps(gprmc, obs):
    obsc = obs.copy()
    try:
        if gprmc.is_fixed() and gprmc.checksum():
            datetime = gprmc.get_date() + " " + gprmc.get_time()
            obsc.date = datetime
            obsc.lat = str(gprmc.get_lat())
            last_lat = str(gprmc.get_lat())
            obsc.lon = str(gprmc.get_lon())
            last_lon = str(gprmc.get_lon())
        return obsc
    except:
        return obs


def setup_serial(port, baud):
    # Set Serial Port - USB0
    ser = serial.Serial(port, baud)
    print("Port used:" + ser.name)
    return ser
#    return SerialTester()

def setup_satellite():
    # Read in TLE for target satellite ICO F2
    icof2 = ephem.readtle('ICO F2',
               '1 26857U 01026A   16172.60175106 -.00000043  00000-0  00000+0 0  9997',
               '2 26857 044.9783   5.1953 0013193 227.2968 127.4685 03.92441898218058')
    return icof2

def to_degrees(radians):
    return radians / ephem.degree

def get_sat_position(icof2, home):
    icof2.compute(home)
    icof2_az = to_degrees(icof2.az)
    icof2_alt = to_degrees(icof2.alt)
    print('Current Satellite Location: Azimuth %3.2f deg, Altitude %3.2f deg' % (icof2_az, icof2_alt))
    return icof2_az, icof2_alt

def read_message(port):
    while True:
        try:
            line = port.readline().decode("ascii").replace('\r', '').replace('\n', '')
        except:
            line = ""
        if len(line) > 0 and line[0] == "$":
            return line

def nmea_tester(sentence):
    mes = nmea.nmea(sentence)
    print("Checksum: ")
    print(mes.checksum())
    print("Reformatted Date & Time: ")
    print(mes.get_date())
    print(mes.get_time())
    print("Lat, Lon: ")
    print(str(mes.get_lat()) + ", " + str(mes.get_lon()))
    print("Heading, MagVar")
    print(str(mes.get_magnetic_heading()) + ", " + str(mes.get_magnetic_var()))


def arduino_tester():
    ard = setup_serial(arduino_port, 115200)
    icof2 = setup_satellite()
    while True:
        try:
            line = read_nmea(ard)
            home = reset()
            home, heading = update(nmea.nmea(line))
            print(home.lat)
            print(home.lon)
            print(home.date)
            print(heading)
        except:
            break

def display_stats(orient, position, obs):
    try:
        print("\n"*65)
        magvar = get_magnetic_var(float(last_lat), float(last_lon))
        print('''               _.:::::._
             .:::'_|_':::.
            /::' --|-- '::\\
           |:" .---"---. ':|
           |: ( O R E O ) :|
           |:: `-------' ::|
            \:::.......:::/
             ':::::::::::'
                `'"""'`\n\n''')
        print("Time: {}\n".format(ephem.now()))

        print('GPS\n===\nFix: {fix}, Lat: {lat}, Lon: {lon}'
              .format(fix = position.is_fixed(), lat = obs.lat, lon = obs.lon))
        print(position.unparsed)

        print("Sensor\n===")
        print('Heading: {heading:7.2f}, Pitch: {pitch:7.2f}, '\
              'Roll: {roll:7.2f}\n---'.format(heading = orient.get_heading(),
                                               pitch = orient.get_pitch(),
                                               roll = orient.get_roll()))
        print('CALIBRATION Sys: {cal[0]}, Gyr: {cal[1]},'\
              ' Acc: {cal[2]}, Mag: {cal[3]}\n'
              .format(cal=orient.get_calibration()))
        print("\nMagnetic Declination: {magvar:7.2f}, "
              "Adjusted Heading: {true_heading:7.2f}"
              .format(magvar = magvar,
              true_heading= (orient.get_heading() +
              magvar+720)%360))
    except:
        pass


def get_magnetic_var(lat, lon):
    gm = geomag.GeoMag()
    magobj = gm.GeoMag(lat, lon)
    return magobj.dec



home = reset()
ard = setup_serial(arduino_port, 115200)
counter = time.time()
f = open("logs/log_"+str(float(ephem.now()))+".csv", 'w')
f.write("Epoch Time,Heading\n")
orient = orientation.orientation("$IMU,0,0,0,0,0,0,0,0,0")
position = nmea.nmea("$GPRMC,0,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
magvar = get_magnetic_var(float(last_lat), float(last_lon))

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    def run(self):
        global val
        global ii
        val = '@'
        ii = ''
        while True:
            ii = input()
            if ii == "q":
                break
            val = chr(ord(val) + 1)
            pass

thread1 = myThread()

thread1.start()

while True:
    mes = (read_message(ard))
    if mes[:2] == "$G":
        try:
            position = nmea.nmea(mes)
        except:
            pass
    elif mes[:2] == "$I":
        try:
            orient = orientation.orientation(mes)
        except:
            pass
    # home.date = "2016-06-28 12:00:00"

        # Operate the antenna if the satellite's elevation is greater than 10
        # degrees
        # If the elevation IS above 10 degrees and the antenna is parked, then
        # unlatch the park_latch variable
    home = update_gps(position, home)
    home.date = ephem.now()

    magvar = get_magnetic_var(float(last_lat), float(last_lon))

    display_stats(orient, position, home)
    print(val)
    if time.time() - counter >= 1.0:
        counter = time.time()
        try:
            heading = orient.get_heading()
            f.write(str(ephem.now())+",")
            f.write(str(heading)+",")
            f.write(val+"\n")
        except:
            f.write("x\n")
    if ii == "q":
        f.close()
        break

'''            icof2_az, icof2_alt = get_sat_position(icof2, home)
            if (icof2_alt >= min_elevation):
                antenna.set_position(icof2_az - heading, icof2_alt)

            else:
                antenna.park()'''
