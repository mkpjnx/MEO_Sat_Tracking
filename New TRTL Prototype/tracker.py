"""Module to read the combined output from the 9-DOF sensor and GPS sensor."""


import serial
import time
import math


def format_date(d):
    """Convert the DDMMYY date format to YYYY/MM/DD format.

    The DDMMYY is returned from the GPS and converted to a format usable by
    PyEphem.
    """
    y = d[4:6]

    if float(y) > 70:
        y = '19' + y

    else:
        y = '20' + y

    return '%s/%s/%s' % (y, d[2:4], d[0:2])


def len_lat_lon(lat):
    """Return length of one degree of latitude and longitude.

    The lengths are a function of latitude.

    Equation taken from http://www.csgnetwork.com/degreelenllavcalc.html
    """
    # Constants for Fourier series approximation
    a1 = 111132.92
    a2 = -559.82
    a3 = 1.175
    a4 = -0.0023
    b1 = 111412.84
    b2 = -93.5
    b3 = 0.118

    lat = math.radians(lat)

    # Fourier seriers that approximates lengths of one degree of lat and long
    lat_len = (a1 + (a2 * math.cos(2 * lat)) +
               (a3 * math.cos(4 * lat)) + (a4 * math.cos(6 * lat)))
    lon_len = ((b1 * math.cos(lat)) + (b2 * math.cos(3 * lat)) +
               (b3 * math.cos(5 * lat)))

    return lat_len, lon_len


def bearing_ll(lat1, lon1, lat2, lon2):
    """Return bearing of vector between two lat/lon points (in degrees E of N).

    Uses linear approximation.
    """
    # Use average of two latitudes to approximate distance
    # (Not very significant at smaller distances)
    lat_len, lon_len = len_lat_lon((lat1 + lat2) / 2)

    x = (lon2 - lon1) * lon_len
    y = (lat2 - lat1) * lat_len

    b = 90 - math.degrees(math.atan2(y, x))  # Bearing in degrees East of North
    return b


def distance_ll(lat1, lon1, lat2, lon2):
    """Return distance between two lat/lon points using linear approximation.

    Distance is in meters.
    """
    lat_len, lon_len = len_lat_lon((lat1 + lat2) / 2)

    x = (lon2 - lon1) * lon_len
    y = (lat2 - lat1) * lat_len

    return ((x * x) + (y * y)) ** .5  # Distance between points in meters


class Tracker:
    """Read and parse serial data from GPS and 9DOF sensors."""

    def __init__(self, port, timeout, baud=9600):
        """Initialize with the provided port and a default baud of 9600."""
        self.ser = serial.Serial(port, baud, timeout = timeout)
        time.sleep(5)
        self.ser.reset_input_buffer()
        self.refresh()
        self.info = ""

    def refresh(self):
        """Return the string read from serial formatted as a list."""
        unparsed = str(self.ser.readline())[2:]
        unparsed = unparsed.replace('\\r', '').replace('\\n', '')

        if len(unparsed.split(',')) < 1:
            print("Timeout occured")
            self.ser.reset_input_buffer()

        else:
            self.info = unparsed.split(',')

    def is_fixed(self):
        """Check fix state of GPS and return True/False."""
        try:
            return self.info[2] == 'A'

        except:
            return False

    def get_lat(self):
        """Get latitude in degrees as a float."""
        try:
            n = self.info.index('N')
            lat_str = self.info[n - 1]
            return float(lat_str[0:2]) + (float(lat_str[2:]) / 60)

        except ValueError:
            try:
                n = self.info.index('S')
                lat_str = self.info[n - 1]
                return -(float(lat_str[0:2]) + (float(lat_str[2:]) / 60))

            except ValueError:
                return None

    def get_lon(self):
        """Return longitude in degrees as a float."""
        try:
            n = self.info.index('E')
            lon_str = self.info[n - 1]
            return float(lon_str[0:3]) + (float(lon_str[3:]) / 60)

        except ValueError:
            try:
                n = self.info.index('W')
                lon_str = self.info[n - 1]
                return -(float(lon_str[0:3]) + (float(lon_str[3:]) / 60))

            except ValueError:
                return None

    def get_time(self):
        """Return current time (in UTC (!!!)) as a formatted string.

        (HH:MM:SS.SSS)
        """
        try:
            if len(self.info[1]) == 10:
                time_str = self.info[1]
                # Format time to HH:MM:SS.SSS
                return time_str[0:2] + ':' + time_str[2:4] + ':' + time_str[4:]

            else:
                return None

        except IndexError:
            return None

    def get_date(self):
        """Get date of latest fix as a formatted string (YYYY/MM/DD)."""
        try:
            if len(self.info[9]) == 6:
                # Format date to YYYY/MM/DD (Compatible with pyephem)
                return format_date(self.info[9])

            else:
                return None

        except IndexError:
            return None

    def get_speed(self):
        """Get speed in knots as a float.

        (Calculated differentially by the GPS unit)
        """
        try:
            return float(self.info[7])

        except IndexError:
            return None

    def get_bearing(self):
        """Get bearing in degres as a float*.

        *GPS actually returns 'Course made good', which is really the direction
        of its movement, and does not necessarily translate to bearing
        """
        try:
            return float(self.info[8])

        except IndexError:
            return None

    def get_magnetic_var(self):  # not sure what these means/how accurate
        """Get magnetic variation at location.

        Add this variation to your magnetic bearing to get true bearing.
        """
        try:
            if self.info[11] == 'E':
                return -float(self.info[10])

            elif self.info[11] == 'W':
                return float(self.info[10])

            else:
                return None

        except IndexError:
            return None

    def get_yaw(self):
        """Get the yaw from the 9-axis sensor as a float."""
        try:
            return float(self.info[13])
        except IndexError:
            return None
        except ValueError:
            return None

    def get_pitch(self):
        """Get the pitch from the 9-axis sensor as a float."""
        try:
            return float(self.info[14])
        except IndexError:
            return None

    def get_roll(self):
        """Get the roll from the 9-axis sensor as a float."""
        try:
            return float(self.info[15])
        except IndexError:
            return None

    def get_sys_cal(self):
        """Get the system calibration from the 9-axis sensor as an int."""
        try:
            return int(self.info[16])
        except IndexError:
            return None

    def get_gyro_cal(self):
        """Get the gyro calibration from the 9-axis sensor as an int."""
        try:
            return int(self.info[17])
        except IndexError:
            return None

    def get_accel_cal(self):
        """Get accelerometer calibration from the 9-axis sensor as an int."""
        try:
            return int(self.info[18])
        except IndexError:
            return None

    def get_mag_cal(self):
        """Get magnetometer calibration from the 9-axis sensor as an int."""
        try:
            return int(self.info[19])
        except IndexError:
            return None

    def checksum(self):
        """Checksum the NMEA sentence to test integrity."""
        a = 0
        tocheck = self.unparsed[1:self.unparsed.index('*')]
        for s in tocheck:
            a ^= ord(s)
        print(self.unparsed.split('*')[1])
        print(str(hex(a)))
        return str(hex(a))[2:] == self.unparsed.split('*')[1]
