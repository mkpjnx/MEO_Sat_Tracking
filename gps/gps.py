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
"""

import serial
import time


class GPS:
    """Provides access to a GPS unit through a serial port.

    ----> Set GPS to ouput GPRMC lines only <----
    Call refresh() function after every sampling iteration to update
    information
    """

    def __init__(self, port, baud):
        """Initialize with the serial port and the baudrate.

        (you will probably want baudrate to be 9600)
        """
        self.ser = serial.Serial(port, baud)

        time.sleep(5)
        self.ser.flushInput()  # Clear out initial junk lines

        self.info = str(self.ser.readline())[2:].split(',')

    def refresh(self):
        """Read most recent line sent by GPS into a list.

        (call this function after every sampling iteration)
        """
        self.info = str(self.ser.readline())[2:].split(',')

    def is_fixed(self):
        """Check fix state of GPS and return True/False."""
        try:
            self.info.index('A')
            return True

        except ValueError:
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
        """Return date of latest fix as a formatted string (DD/MM/YY)."""
        try:
            if len(self.info[9]) == 6:
                date_str = self.info[9]
                # Format date to DD/MM/YY
                return date_str[0:2] + '/' + date_str[2:4] + '/' + date_str[4:]

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
