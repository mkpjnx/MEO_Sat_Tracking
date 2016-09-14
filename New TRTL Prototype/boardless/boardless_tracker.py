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
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(5)
        self.ser.reset_input_buffer()
        self.info = ""
        self.refresh()

    def refresh(self):
        """Return the string read from serial formatted as a list."""
        # time.sleep(1)
        unparsed = str(self.ser.readline())
        unparsed = unparsed.replace('\\r', '').replace('\\n', '').replace('b', '').replace("'", '')
        self.info = unparsed.split(',')
        # if len(unparsed.split(',')) < 20:
        #     print("Timeout occured")
        #     self.ser.reset_input_buffer()
        #
        # else:
        #     self.info = unparsed.split(',')
        print(self.info)

    def is_fixed(self):
        """Pretend the module is always fixed."""
        return True

    def get_lat(self):
        """Get lat."""
        try:
            return float(self.info[1])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_lon(self):
        """Get lon."""
        try:
            return float(self.info[2])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_yaw(self):
        """Get yaw."""
        try:
            return float(self.info[3])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_true(self):
        """Get true bearing."""
        try:
            return float(self.info[4])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_time(self):
        """Get lon."""
        return self.info[0]
