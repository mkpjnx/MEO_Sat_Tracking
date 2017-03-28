"""Standalone TRTL algorithm module."""
import time
from threading import Thread
import serial
import sentences
import geolists

def setup_serial(port: str, baud: int) -> serial.Serial:
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

def display_stats(position_nmea: sentences.NMEA, gain_adc: sentences.ADC, bearing_list) -> None:
    """Display the current GPS and heading data."""
    print('GPS\n===\nFix: {fix}, Lat: {lat}, Lon: {lon}'
          .format(fix=position_nmea.is_fixed(),
                  lat=position_nmea.get_lat(),
                  lon=position_nmea.get_lon()))
    print(position_nmea.unparsed)
    print("===\nCurrent Gain: {gain:7.2f}".format(gain=gain_adc.get_gain()))
    print("===\nCurrent Bearing: {bear:7.2f}".format(bear=bearing_list.get_bearing()))

ARDUINO_PORT = 'COM3'
ARDUINO_BAUD = 115200
UPDATE_RATE = 5.0
ARDUINO = setup_serial(ARDUINO_PORT, ARDUINO_BAUD)
INITIAL_LAT = 0
INITIAL_LON = 0
INITIAL_HEADING = 0
DISTANCE_THRESHOLD = 1

class AlgorithmThread(Thread):
    """The algorithm wrapped in a thread."""
    def __init__(self):
        """Inherit thread properties."""
        Thread.__init__(self)
        self.data = {"heading": INITIAL_HEADING, "lat": INITIAL_LAT, "lon": INITIAL_LON, "gain": 0}
    def run(self) -> None:
        """Main heading determination algorithm."""
        position = sentences.NMEA()
        gain_sentence = sentences.ADC()

        coords_list = geolists.CoordsList(INITIAL_LAT, INITIAL_LON)
        bearing_list = geolists.BearingList(INITIAL_HEADING)

        last_time = time.time()

        time_string = time.strftime("%d-%m-%Y_%H-%M-%S", time.localtime())

        with open(time_string + ".csv", "w") as log:
            log.write("Time, Lat, Lon, Heading, Diffbearing\n")

            while True:
                sentence = read_message(ARDUINO)
                if sentence[:2] == "$G":
                    try:
                        position = sentences.NMEA(sentence)
                        # travelled_distance = coords_list.get_dist_travelled()
                        if position.is_fixed():
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
                gain = gain_sentence.get_gain()
                bearing = str(bearing_list.get_bearing())

                display_stats(position, gain_sentence, bearing_list)

                if time.time() - last_time >= UPDATE_RATE:
                    last_time = time.time()
                    # log.write(", ".join(
                    #     [str(x) for x in [last_time, lat, lon, bearing, gain]]) + "\n")
                    self.data = {"heading": bearing, "lat": lat, "lon": lon, "gain": gain}
                    # print(self.data)
TRTL = AlgorithmThread()
TRTL.start()
