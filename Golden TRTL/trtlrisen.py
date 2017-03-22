"""Standalone TRTL algorithm module."""
import time
from threading import Thread
import serial
import sentences
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

class AlgorithmThread(Thread):
    """The algorithm wrapped in a thread."""
    def __init__(self):
        """Inherit thread properties."""
        Thread.__init__(self)
        self.data = {"heading": 0, "lon": 0, "lat": 0, "gain": 0}
    def run(self) -> None:
        """Main heading determination algorithm."""
        position = sentences.NMEA()
        gain_sentence = sentences.ADC()

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
                        position = sentences.NMEA(sentence)
                        if position.is_fixed() and position.get_speed() > 1:
                            coords_list.add_coords(position.get_lat(), position.get_lon())
                            bearing_list.add_bearing(coords_list.get_current_bearing())
                        else:
                            coords_list.lock()
                            bearing_list.lock()
                    except (IndexError, geolists.UnchangedPointError) as gps_error:
                        print("GPS ERROR: {0}".format(gps_error))
                elif sentence[:2] == "$A":
                    gain_sentence = sentences.ADC(sentence)



                lat = str(position.get_lat())
                lon = str(position.get_lon())
                # heading = str(orientation.get_heading())
                gain = gain_sentence.get_gain()
                bearing = str(bearing_list.get_bearing())


                if time.time() - last_time >= 1.0:
                    last_time = time.time()
                    log.write(", ".join([str(x) for x in [lat, lon, bearing, gain]]) + "\n")
                    self.data = {"heading": bearing, "lon": lon, "lat": lat, "gain": gain}

TRTL = AlgorithmThread()
TRTL.start()
