"""Main algorithm for bearing calculation."""

import threading
import time
import ephem
import serial

import nmea
import orientation
import geolists

from geolists import rotate_check  # , drift_check

from geomag import geomag

# Constants
INITIAL_AZ = 180
INITIAL_ALT = 90
MIN_ELEVATION = 10.0  # Horizon for antenna
SLEEP_TIME = 1.0
UNWIND_THRESHOLD = 180
SLEEP_ON_UNWIND = 45.0

last_lon = '-88.787'
last_lat = '41.355'
last_heading = 0.0

# Please make sure these are set correctly
mount_port = '/dev/ttyUSB0'
mount_baud = 9600

# arduino_port = '/dev/ttyACM0'
arduino_port = 'COM4'
arduino_baud = 115200


class SerialTester:
    """Tester class for serial writing and reading."""

    def write(self, line):
        """Print to terminal instead of writing to serial."""
        print(line)

    def read(self):
        """Return nothing."""
        return


def reset():
    """Create the observer object."""
    obs = ephem.Observer()
    # Set LAT/LON Coordinates to IMSA's location
    obs.date = ephem.now()
    obs.lon = last_lon
    obs.lat = last_lat
    obs.elevation = 0.0
    return obs


def update_gps(gprmc, obs):
    """Update the observer with new GPS coordinates."""
    obs.date = ephem.now()  # update time anyway
    obsc = obs.copy()  # deep copy
    try:
        if gprmc.is_fixed() and gprmc.checksum():
            datetime = gprmc.get_date() + " " + gprmc.get_time()
            obsc.date = datetime
            obsc.lat = str(gprmc.get_lat())
            last_lat = str(gprmc.get_lat())
            obsc.lon = str(gprmc.get_lon())
            last_lon = str(gprmc.get_lon())
        return obsc
    except Exception:
        return obs


def setup_serial(port, baud):
    """Create the Serial object."""
    ser = serial.Serial(port, baud)
    print("Port used:" + ser.name)
    return ser


def setup_satellite():
    """Read in TLE for target satellite ICO F2."""
    icof2 = ephem.readtle(
        'ICO F2',
        '1 26857U 01026A   16172.60175106 -.00000043  00000-0  00000+0 0  9997',
        '2 26857 044.9783   5.1953 0013193 227.2968 127.4685 03.92441898218058')
    return icof2


def get_sat_position(icof2, home):
    """Return the azimuth and altitude of the satellite."""
    icof2.compute(home)
    azi = icof2.az / ephem.degree
    alt = icof2.alt / ephem.degree
    print('Current Satellite Location: Azimuth %3.2f deg, Altitude %3.2f deg' %
          (icof2.az, icof2.alt))
    return azi, alt


def read_message(port):
    """."""
    while True:
        try:
            line = port.readline().decode("ascii").replace('\r', '').replace(
                '\n', '')
        except:
            line = ""
        if len(line) > 0 and line[0] == "$":
            return line


def display_stats(orient, position, obs, bearing, status):
    """Print the current values to the console."""
    try:
        # print("\n"*65)
        magvar = get_magnetic_var(float(last_lat), float(last_lon))
        # print('''               _.:::::._
        #      .:::'_|_':::.
        #     /::' --|-- '::\\
        #    |:" .---"---. ':|
        #    |: (GLDN TRTL) :|
        #    |:: `-------' ::|
        #     \:::.......:::/
        #      ':::::::::::'
        #         `'"""'`\n\n''')
        print("Time: {}\n".format(ephem.now()))

        print('GPS\n===\nFix: {fix}, Lat: {lat}, Lon: {lon}'
              .format(fix=position.is_fixed(), lat=obs.lat, lon=obs.lon))
        print(position.unparsed)

        print("Sensor\n===")
        print('Heading: {heading:7.2f}, Pitch: {pitch:7.2f}, '
              'Roll: {roll:7.2f}\n---'.format(heading=orient.get_heading(),
                                              pitch=orient.get_pitch(),
                                              roll=orient.get_roll()))
        print('CALIBRATION Sys: {cal[0]}, Gyr: {cal[1]},'
              ' Acc: {cal[2]}, Mag: {cal[3]}\n'
              .format(cal=orient.get_calibration()))
        print("\nMagnetic Declination: {magvar:7.2f}, "
              "Adjusted Heading: {true_heading:7.2f}"
              .format(magvar=magvar,
                      true_heading=(orient.get_heading() + magvar+720) % 360))
        print("\nCurrent Bearing: {bear:7.2f}, "
              "Bearing Method: {method}".format(bear=bearing, method=status))
        print("\nSubinterval: {subint}".format(subint=val))
    except Exception:
        pass


def get_magnetic_var(lat, lon):
    """Get the magnetic variation."""
    gm = geomag.GeoMag()
    magobj = gm.GeoMag(lat, lon)
    return magobj.dec


def nmea_tester(sentence):
    """Print a formatted NMEA sentence."""
    mes = nmea.NMEA(sentence)
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
    """Test arduino setup."""
    ard = setup_serial(arduino_port, 115200)
    icof2 = setup_satellite()  # NOQA
    while True:
        try:
            line = read_nmea(ard)
            home = reset()
            home, heading = update(nmea.NMEA(line))
            print(home.lat)
            print(home.lon)
            print(home.date)
            print(heading)
        except:
            break


# initialize observer and ports
home = reset()
ard = setup_serial(arduino_port, arduino_baud)
# ant = antenna.Antenna(mount_port, mount_baud) #Use this later

# These variables hold objects with all of the data related to orientation from
# the DOF and position from the NMEA.
orient = orientation.Orientation("$IMU,0,0,0,0,0,0,0,0,0")
position = nmea.NMEA("$GPRMC,0,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

magvar = get_magnetic_var(float(last_lat), float(last_lon))
counter = time.time()

# List of GPS coordinates for calculating bearing differentially
coords_list = geolists.CoordsList(float(last_lat), float(last_lon))

coords_br_list = geolists.BearingList(last_heading)  # GPS bearings
# dof_br_list = geolists.BearingList(orient.get_heading())  # DOF bearings
# nmea_br_list = geolists.BearingList(position.get_bearing())  # NMEA bearings


class KeyListener(threading.Thread):
    """Class to run the algorithm while waiting for key presses."""

    def __init__(self):
        """Inherit the threading stuff."""
        threading.Thread.__init__(self)

    def run(self):
        """Listen for keys."""
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


kl = KeyListener()

kl.start()
with open(str(float(ephem.now()))+".csv", 'w') as f:
    f.write("Time, Latitude, Longitude, Heading, DOF Bearing, NMEA Bearing,"
            "Differential Bearing, Interval\n")
    while True:

        # Updates whenever data comes in
        mes = (read_message(ard))
        if mes[:2] == "$G":
            try:
                print("GPS received")
                position = nmea.NMEA(mes)
                coords_list.add_coords(position.get_lat(), position.get_lon())
                coords_br_list.add_bearing(coords_list.get_current_bearing())
                # nmea_br_list.add_bearing(position.get_bearing())
                print("GPS parsed")
            except Exception as e:
                print("GPS ERROR: {0}".format(e))
        elif mes[:2] == "$I":
            try:
                # print("Orientation received")
                orient = orientation.Orientation(mes)
                corrected_heading = (orient.get_heading() + magvar + 720) % 360
                # dof_br_list.add_bearing(corrected_heading)
                # print("Orientation parsed")
            except Exception as e:
                print("ORIENTATION ERROR: {0}".format(e))

        home = update_gps(position, home)
        home.date = ephem.now()

        magvar = get_magnetic_var(float(last_lat), float(last_lon))
        mag_cal = float(orient.get_calibration()[3])

        # Bearing decision starts here using the differential method by default
        bearing = coords_br_list.get_bearing()
        method = "TRTL Differential"

        # Debug the length of the bearing lists
        # print(len(dof_br_list.b), len(coords_br_list.b), len(nmea_br_list.b))

        # Decide on which method to use
        # if mag_cal > 0 and len(dof_br_list.b) > 1:
        #     if rotate_check(dof_br_list, 2):
        #         bearing = nmea_br_list.get_bearing()
        #         method = "NMEA Bearing"
        #     else:
        #         bearing = dof_br_list.get_bearing()
        #         method = "DOF Heading"

        # Print the stats
        display_stats(orient, position, home, bearing, method)

        if time.time() - counter >= 1.0:
            counter = time.time()
            try:
                f.write(str(ephem.now()) + ", " +
                        str(position.get_lat()) + ", " +
                        str(position.get_lon()) + ", " +
                        str(orient.get_heading()) + ", " +
                        # str(dof_br_list.get_bearing()) + ", " +
                        # str(nmea_br_list.get_bearing()) + ", " +
                        str(coords_br_list.get_bearing()) + ", " +
                        val+"\n")
            except Exception as ex:
                print("WRITE ERROR: {0}".format(ex))
                f.write("ERROR\n")
        if ii == "q":
            break

    # icof2_az, icof2_alt = get_sat_position(icof2, home)
    # antenna.set_position(icof2_az - heading, icof2_alt)
