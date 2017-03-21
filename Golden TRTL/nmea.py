"""This module provides a class and util function for parsing NMEA sentences.

Takes in a $GPRMC sentence and parses it for information.
Slightly modified version of the original GPS.py code.
"""


def format_date(date: str):
    """Convert the DDMMYY date format returned by the GPS.

    Converts to the YYYY/MM/DD format that is compatible with pyephem.
    """
    year = date[4:6]

    if float(year) > 70:
        year = '19' + year

    else:
        year = '20' + year

    return '%s/%s/%s' % (year, date[2:4], date[0:2])


class NMEA:
    """Read and parse a $GPRMC sentence.

    Set GPS to ouput GPRMC lines only!
    """

    def __init__(self, sentence: str="$GPRMC,0,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"):
        """Initialize with the unparsed sentence."""
        self.unparsed = sentence
        self.info = sentence.split(',')

    def is_fixed(self):
        """Check fix state of GPS and return True/False."""
        try:
            return self.info[2] == 'A'
        except IndexError:
            return False

    def get_lat(self):
        """Return latitude in degrees as a float."""
        try:
            ind = self.info.index('N')
            lat_str = self.info[ind - 1]
            return float(lat_str[0:2]) + (float(lat_str[2:]) / 60)

        except ValueError:
            try:
                ind = self.info.index('S')
                lat_str = self.info[ind - 1]
                return -(float(lat_str[0:2]) + (float(lat_str[2:]) / 60))

            except ValueError:
                return None

    def get_lon(self):
        """Return longitude in degrees as a float."""
        try:
            ind = self.info.index('E')
            lon_str = self.info[ind - 1]
            return float(lon_str[0:3]) + (float(lon_str[3:]) / 60)

        except ValueError:
            try:
                ind = self.info.index('W')
                lon_str = self.info[ind - 1]
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

    def get_split(self):
        """Return the split info."""
        return self.info

    def checksum(self):
        """Check for malformed sentences."""
        commacount = 12
        try:
            return self.unparsed.count(',') == commacount
        except TypeError:
            return False
