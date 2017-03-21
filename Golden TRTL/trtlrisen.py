"""Standalone TRTL algorithm module."""
import time
import serial
import nmea
import orientation as orient
import geolists

ARDUINO_PORT = 'COM4'
ARDUINO_BAUD = 115200
ARDUINO = setup_serial(ARDUINO_PORT, ARDUINO_BAUD)

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
    position = nmea.NMEA("$GPRMC,0,V,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    orientation = orient.Orientation("$IMU,0,0,0,0,0,0,0,0,0")

    coords_list = geolists.CoordsList(0, 0)
    bearing_list = geolists.BearingList(0)

    last_time = time.time()

    time_string = time.strftime("%d-%m-%Y_%H-%M-%S", time.localtime())

    with open(time_string + ".csv") as log:
        log.write("Time, Lat, Lon, Heading, Diffbearing\n")

        while True:
            sentence = read_message(ARDUINO)
            if sentence[:2] == "$G":
                try:
                    position = nmea.NMEA(sentence)
                    coords_list.add_coords(position.get_lat(), position.get_lon())
                    bearing_list.add_bearing(coords_list.get_current_bearing())
                except IndexError as gps_error:
                    print("GPS ERROR: {0}".format(gps_error))
            elif sentence[:2] == "$I":
                orientation = orient.Orientation(sentence)

            lat = str(position.get_lat())
            lon = str(position.get_lon())
            heading = str(orientation.get_heading())
            bearing = str(bearing_list.get_bearing())

            if time.time() - last_time >= 1.0:
                last_time = time.time()
                log.write(", ".join([str(x) for x in [lat, lon, heading, bearing]]) + "\n")

if __name__ == '__main__':
    main()
