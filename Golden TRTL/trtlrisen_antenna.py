"""Standalone TRTL algorithm module."""
import time
from os import system
import serial
import ephem
import nmea
# import orientation as orient
import geolists
import antenna

ARDUINO_PORT = 'COM4'
ARDUINO_BAUD = 115200
ARDUINO = setup_serial(ARDUINO_PORT, ARDUINO_BAUD)


def update_observer(observer: ephem.Observer, new_nmea: nmea.NMEA) -> ephem.Observer:
    """Update the Observer with new NMEA data."""
    if new_nmea.is_fixed() and new_nmea.checksum():
        new_observer = observer.copy()
        new_observer.date = new_nmea.get_date() + " " + new_nmea.get_time
        new_observer.lat = str(new_nmea.get_lat())
        new_observer.lon = str(new_nmea.get_lon())

        # Synchronize the system clock with the time from the sentence.
        # If there is a bad sentence, the time will stay accurate
        # so we can safely fall back on ephem.now()
        # Comment this out if you're not using the Raspberry Pi.
        system("date --set %s" % str(new_observer.date))

        return new_observer
    else:
        observer.date = ephem.now()
        return observer

def setup_satellite() -> ephem.Body:
    """Get the Body for the ICO F2 satellite from its TLE."""
    satellite = ephem.readtle(
        'ICO F2',
        '1 26857U 01026A   16172.60175106 -.00000043  00000-0  00000+0 0  9997',
        '2 26857 044.9783   5.1953 0013193 227.2968 127.4685 03.92441898218058')
    return satellite

def get_satellite_position(satellite: ephem.Body, observer: ephem.Observer):
    """Get the azimuth and altitude of the satellite."""
    satellite.compute(observer)
    azimuth = satellite.az / ephem.degree
    altitude = satellite.alt / ephem.degree
    print("Satellite location: Azimuth %3.2f° Altitude %3.2f°" % (satellite.az, satellite.alt))
    return azimuth, altitude

def setup_serial(port: str, baud: int) -> None:
    """Create the Serial object."""
    ser = serial.Serial(port, baud)
    print("Port used:" + ser.name)
    return ser

def read_message(serial_port: serial.Serial) -> str:
    """Read in, decode, and return a sentence from the serial port."""
    while True:
        try:
            line = serial_port.readline().decode("ascii").replace('\r', '').replace('\n', '')
        except UnicodeError:
            line = ""
        if len(line) > 0 and line[0] == "$":
            return line

def main() -> None:
    """Main heading determination algorithm."""
    position = nmea.NMEA()
    ground_point = ephem.Observer()
    ico_f2 = setup_satellite()
    target_antenna = antenna.Antenna()
    # A linter will probably complain about these next few lines.
    # Blame PyEphem, they're otherwise fine.
    ground_point.date = ephem.now()
    ground_point.lat = str(position.get_lat())
    ground_point.lon = str(position.get_lon())
    ground_point.elevation = 0.0

    # orientation = orient.Orientation()

    coords_list = geolists.CoordsList(0, 0)
    bearing_list = geolists.BearingList(0)

    last_time = time.time()
    time_string = time.strftime("%d-%m-%Y_%H-%M-%S", time.localtime())

    with open(time_string + ".csv") as log:
        log.write("Time, Lat, Lon, Calculated Bearing, NMEA Bearing\n")

        while True:
            sentence = read_message(ARDUINO)
            if sentence[:2] == "$G":
                try:
                    position = nmea.NMEA(sentence)
                    coords_list.add_coords(position.get_lat(), position.get_lon())
                    bearing_list.add_bearing(coords_list.get_current_bearing())
                    ground_point = update_observer(ground_point, position)

                except IndexError as gps_error:
                    print("GPS ERROR: {0}".format(gps_error))
            elif sentence[:2] == "$I":
                # orientation = orient.Orientation(sentence)
                pass

            lat = str(position.get_lat())
            lon = str(position.get_lon())
            # heading = str(orientation.get_heading())
            d_bearing = str(bearing_list.get_bearing())  # Calculated bearing
            n_bearing = str(position.get_bearing())  # NMEA bearing

            # Logging
            if time.time() - last_time >= 1.0:
                last_time = time.time()
                log.write(", ".join([str(x) for x in [lat, lon, d_bearing, n_bearing]]) + "\n")

            target_azimuth, target_altitude = get_satellite_position(ico_f2, ground_point)
            target_antenna.move(target_azimuth, target_altitude)

if __name__ == '__main__':
    main()
