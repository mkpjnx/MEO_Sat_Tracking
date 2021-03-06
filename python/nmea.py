"""Slightly modified version of the original GPS.py code

The nmea class takes in a $GPRMC sentence and parses it for information
"""

import time
import math
import ephem
from geomag import geomag

def format_date(d):
    """Convert the DDMMYY date format returned by the gps to
       a YYYY/MM/DD format that is compatible with pyephem
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
    """Return bearing of vector between two lat/lon points. (In degrees E of N)

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


class nmea:
    """reads and parses a $GPRMC sentence.

    ----> Set GPS to ouput GPRMC lines only <----
    Create new nmea
    """

    def __init__(self, sentence):
        '''Initialize with the unparsed sentence'''
        self.unparsed = sentence
        self.info = sentence.split(',')

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
            time_str = self.info[1]
            # Format time to HH:MM:SS.SSS
            return time_str[0:2] + ':' + time_str[2:4] + ':' + time_str[4:]

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

    def get_magnetic_var(self):  # not sure what these mean/how accurate
        """Return magnetic variation at location.

        Add this variation to your magnetic bearing to get true bearing.
        """
        try:
            print("found mag")
            gm = geomag.GeoMag()
            magobj = gm.GeoMag(self.get_lat(),self.get_lon())
            return magobj.dec
        except IndexError:
            return None

    def get_split(self):
        return self.info
        
    def checksum(self):
        commacount = 12
        try:
            return self.unparsed.count(',') == commacount
        except:
            return False
