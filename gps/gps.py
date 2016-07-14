"""Access a GPS module through a serial port and parse the data.

A python library to accessing a GPS module through a serial port and parsing
the data for desirable information.

In order for it to work properly, there are a few settings you need to
manipulate in your GPS and your code
1. Set GPS unit to output GPRMC (Recommended Minimum) data only

2. Set the output frequency of your GPS to coincide with the sampling interval
in your code in order to properly read all lines sent by the GPS without buffer

3. Make sure to call the refresh() function of the GPS after every sampling
iteration in your code in order to properly access the most recent information
sent by the GPS

4. You should only try to read data from the GPS if the fix state is True, but
if for any reason the GPS sends strange data the class will return None for any
missing values

Sources:
http://www.csgnetwork.com/degreelenllavcalc.html <-- For distance of lat/lon calculator
"""

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


class GPS:
    """Provides access to a GPS unit through a serial port.

    ----> Set GPS to ouput GPRMC lines only <----
    Call refresh() function after every sampling iteration to update
    information
    """

    def __init__(self, port, baud=9600):
        """Initialize with the serial port and the baudrate."""
        self.ser = serial.Serial(port, baud)

        time.sleep(5)
        self.ser.reset_input_buffer()  # Clear out initial junk lines

        self.unparsed = str(self.ser.readline())[2:]
        # Clean out junk characters and newlines
        self.unparsed = self.unparsed.replace('\r', '').replace('\n', '')
        self.info = self.unparsed.split(',')

    def refresh(self):
        """Read most recent line sent by GPS into a list.

        (call this function after every sampling iteration)
        """
        self.info = str(self.ser.readline())[2:].split(',')

    def is_fixed(self):
        """Check fix state of GPS and return True/False."""
        try:
            return self.info[2] == 'A'
        except:
            return False

    def get_lat(self):
        """Return latitude in degrees as a float."""
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
        """Return date of latest fix as a formatted string (YYYY/MM/DD)."""
        try:
            if len(self.info[9]) == 6:
                # Format date to YYYY/MM/DD (Compatible with pyephem)
                return format_date(self.info[9])

            else:
                return None

        except IndexError:
            return None

    def get_speed(self):
        """Return speed in knots as a float.

        (Calculated differentially by the GPS unit)
        """
        try:
            return float(self.info[7])

        except IndexError:
            return None

    def get_bearing(self):
        """Return bearing in degres as a float*.

        *GPS actually returns 'Course made good', which is really the direction
        of its movement, and does not necessarily translate to bearing
        """
        try:
            return float(self.info[8])

        except IndexError:
            return None

    def get_magnetic_var(self):  # not sure what these means/how accurate
        """Return magnetic variation at location.

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

    def checksum(self):
        """Checksum the NMEA sentence to test integrity."""
        a = 0
        tocheck = self.unparsed[1:self.unparsed.index('*')]
        for s in tocheck:
            a ^= ord(s)
        print(self.unparsed.split('*')[1])
        print(str(hex(a)))
        return str(hex(a))[2:] == self.unparsed.split('*')[1]
