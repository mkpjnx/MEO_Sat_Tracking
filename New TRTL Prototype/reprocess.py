"""Read in data from a text file and process it using the algorithm.

Current output line format:
TIME, LAT, LON, CALC_BEARING, HEADING, STATUS

"""
import tracker
import header


class Transcriber:
    """docstring for Transcriber."""

    def __init__(self, file_in=input("Input file name: ")):
        """Constructor."""
        self.file_in = file_in
        self.lat_list = []
        self.lon_list = []
        self.ang_list = []

    def generate_data(self):
        """Read a line and extract the variables."""
        with open(self.file_in) as f:
            for line in f:
                data_list = line.replace('\n', '').split(',')
                try:
                    # print(data_list[1], data_list[2], data_list[4])
                    self.lat_list.append(data_list[1])
                    self.lon_list.append(data_list[2])
                    self.ang_list.append(data_list[4])
                except IndexError:
                    print(data_list[0])

tr = Transcriber(file_in='2016-08-04_18-11-10.000.txt')
tr.generate_data()
