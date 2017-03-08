"""Run the differential method with GPS data."""
import csv
from time import time
import geolists

LAT = 0
LON = 1

def main():
    """The that thing."""
    # These are just values to make accessing the 2D list of coords more readable.


    processed_bearings = []  # Create the list of calculated bearings.
    # This is used to write to file later.

    # Read in the test data and store it in the space_list.
    with open('moredata.csv', 'r') as file:
        reader = csv.reader(file)
        space_list = list(reader)  # IMPORTANT: This list is full of strings!
    print(space_list)
    # Behold, my ultimate list comprehension to convert everything to float!
    space_list = [[float(y) for y in x] for x in space_list]

    # Create the list objects. Look into initilizing these with better values.
    coords_list = geolists.CoordsList(space_list[0][LAT], space_list[0][LON])
    bearing_list = geolists.BearingList(0)

    for pair in space_list:
        # Add the latest coordpair to the coordlist.
        coords_list.add_coords(pair[LAT], pair[LON])
        # Add the calculated bearing from that coordpair to bearinglist.
        bearing_list.add_bearing(coords_list.get_current_bearing())
        # And add that bearing to our final list.
        processed_bearings.append(bearing_list.get_bearing())

    # Write to the output file.
    with open("output_" + str(time()) + ".csv", 'w') as out:
        for item in processed_bearings:
            out.write(str(item) + "\n")

if __name__ == "__main__":
    main()
