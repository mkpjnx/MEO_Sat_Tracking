"""A module to provide interfaces with the antenna mount."""
from serial import Serial


# Constants
INITIAL_AZ = 180
INITIAL_ALT = 90
MIN_ELEVATION = 5.0
SLEEP_TIME = 1.0
STEPS_PER_ALT_DEG = 8.0 / 3.0
STEPS_PER_AZ_DEG = 40.0 / 9.0
MOUNT_PORT = '/dev/ttyUSB0'
MOUNT_BAUD = 9600

class SerialTester:
    """A class that provides dummy functions to see what will be written to the serial port."""
    @staticmethod
    def write(line):
        """Print out the expected written serial data."""
        print(line)

    @staticmethod
    def read(num):
        """Pass on read."""
        pass


class Antenna:
    """A class for writing to the antenna serial port to position the antenna."""
    def __init__(self, port: str=MOUNT_PORT, baud: int=MOUNT_BAUD):
        """Initialize with the unparsed sentence."""
        self.azimuth = INITIAL_AZ
        self.altitude = INITIAL_ALT
        self.parked = True
        self.ser = Serial(port, baud)

    def set_position(self, azi: float, alt: float) -> None:
        """Convert azimuth and altitude angles to steps and write to the antenna serial port."""
        steps_alt = round((alt - self.altitude) * STEPS_PER_ALT_DEG)
        steps_azi = round((azi - self.azimuth) * STEPS_PER_AZ_DEG)
        self.azimuth = azi
        self.altitude = alt
        self.ser.write("{},{}".format(steps_alt, steps_azi))
        self.ser.read(64)

    def park(self):
        """Return the antenna to the initial angles."""
        if self.parked:
            print('Antenna Parked')
        else:
            print('Parking Antenna')
            self.set_position(INITIAL_AZ, INITIAL_ALT)
            self.parked = True

    def move(self, azi: float, alt: float):
        """Move the antenna to the angles if the azimuth is above the minimum elevation."""
        if azi >= MIN_ELEVATION:
                    # Unwrap Cable if Azimuth will cross through True North
                    # In the above case, Set Azimuth to 180 Degrees, then pick up
                    # normal tracking
                    # Then sleep 45 seconds to give the positioner time to
                    # reposition
            print('Tracking Mode')
            self.set_position(azi, alt)
        else:
            self.park()
