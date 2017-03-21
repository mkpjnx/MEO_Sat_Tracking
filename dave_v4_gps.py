import time
import ephem
import serial
import io
import sys
import string
import math
import pdb

from datetime import datetime

####################################################

def convertAlt(num1):
    x = num1
    steps = x * 2.6666 #8/3: every eight steps is 3 degrees
    steps = int(round(steps))
    return steps

def convertAz(num1):
    x = num1
    steps = x * 4.4444 #40/9: every 40 steps is 9 degrees???
    steps = int(round(steps))
    return steps

def convertDec(deg, dir):
    decVal = 0.0
    if(dir == "lon"):
        degs = deg[0:3]
        hours = deg[3:]
    else:
        degs = deg[0:2]
        hours = deg[2:]

    decVal = int(degs) + (float(hours) / 60)
    decVal = round(decVal, 4)
    return decVal

### Function to obtain Heading from GPS
def getGPSinfo():
    gps_info ={'heading' : 0.0, 'lat' : 46.8152, 'lon' : -71.2077 }

    #Get USB port
    #try:
    gpsSer = serial.Serial()
    gpsSer.baudrate = 19200
    gpsSer.timeout = 10
    gpsSer.port = '/dev/ttyUSB0'
    gpsSer.open()

    getInfo = True
    gotAll = 0

        #Read GPS input until get Heading "$HEHDT"
    while getInfo:
        thisLn = gpsSer.readline()


        if(thisLn.find("$HEHDT") >= 0):
            hLst = thisLn.split(",")
            if(hLst[1] != ""):
                gps_info['heading'] = float(hLst[1]) #Obtain Heading in DEG
            gotAll = gotAll + 1

        if(thisLn.find("$GPGGA") >= 0):
            hLst = thisLn.split(",")
            print(hLst[2])
            print(hLst[4])
            gps_info['lat'] = convertDec(hLst[2], "lat")
            gps_info['lon'] = -1 * convertDec(hLst[4], "lon")
            gotAll = gotAll + 1

        if(gotAll >=2):
            getInfo = False

    gpsSer.close()

    #except:
        #print("Error: Could not connect to GPS")

    return gps_info

####################################################

gps_values = getGPSinfo()

dpr = 180.0 / math.pi     # dpr = degrees per radian

home = ephem.Observer()

#home.lon = '-71.2077'
home.lon = str(gps_values['lon'])     #Init Longitud with current postion

#home.lat = '46.8152'
home.lat = str(gps_values['lat']) #Init Latitud with current postion

home.elevation = 300

alt = 0
az = 0

altVal = 0
azVal = 0

steps_az = steps_alt = 0
last_alt_steps_value = 0
last_az_steps_value = 0

# Set Serial Port - Arduino Serial Port
ser = serial.Serial('/dev/ttyACM0', 9600)

# Read in TLE for target satellite ICO F2
icof2 = ephem.readtle('ICO F2',
                             '1 26857U 01026A     17046.22129146 -.00000042    00000-0    00000+0 0    9998',
                             '2 26857    44.9271 310.0735 0015801 300.3176 244.6837    3.92441859227461')

# Compute satellite's position every 10 seconds

while True:

    ######    Get current GPS values
    gps_values = getGPSinfo()

    heading_deg = gps_values['heading']    #Obtaing heading in Degs
    home.lon = str(gps_values['lon']) #Update Longitud with current postion

    # printing current log and lat
    home.lat = str(gps_values['lat'])    #Update Latitud with current postion

    home.date = datetime.utcnow()

    icof2.compute(home)

    print (icof2.az )
    print(gps_values)
    # Changes to convert satellite azimuth string value to a float value
    icof2_str = str(icof2.az)
    # Casting angle object from ephem into a string to convert in a float
    split_degs = icof2_str.split(':')
    degs_int = float(split_degs[0])
    degs_int = degs_int + (float(split_degs[1])/60)
    print (degs_int)

    icof2_az_deg = icof2.az * dpr


    icof2_alt_deg = icof2.alt * dpr


    icof2_az_deg = 360 - (heading_deg - degs_int)    #TAKE HEADING FROM CURRENT AZIMUTH
    print (icof2_az_deg)
    if(icof2_az_deg > 360):
        icof2_az_deg = icof2_az_deg - 360
        print (icof2_az_deg)


    print('Current Location: Azimuth %3.2f deg, Altitude %3.2f deg, Heading %3.2f' % (icof2_az_deg, icof2_alt_deg, heading_deg))
    icof2_az_integer = int(round(icof2_az_deg))
    icof2_alt_integer = int(round(icof2_alt_deg))

    # If the satellite's elevation is greater than 5 degrees do the following

    if (icof2_alt_deg >= 5.00):

        print ('Tracking Active ')


        # Convert    Altitude to integer number
        alt = icof2_alt_integer

        print('Integer Altitude: %3i deg' % (alt))

        # Compute total number of steps needed for current Altitude - altVal is represented in STEPS
        altVal = convertAlt(alt)
        print('Total Altitude Steps Required: %4i' % (altVal))

        # Compute number of steps needed to move this time - last steps total minus this steps total
        steps_alt = altVal - last_alt_steps_value
        print('Steps to move in Altitude: %3i' % (steps_alt))

        # Convert Azimuth to integer number
        az = icof2_az_integer
        print('Initial Azimuth integer: %3i' % (az))

        # Compute total number of steps needed for current Azimuth - azVal is represented in STEPS
        azVal = convertAz(az)
        print('Total steps for Azimuth: %4i' % (azVal))

        # Compute total number of steps needed to move this time - last steps minus this steps
        steps_az = azVal - last_az_steps_value


        val1 = str(steps_alt)
        val2 = str(steps_az)

        values = val1 + "," + val2
        print(values)
        ser.write(values)

        # Update total number of steps
        last_alt_steps_value = altVal
        last_az_steps_value = azVal

        deg_alt = altVal / 2.6666
        deg_az = azVal / 4.4444

        print('\t Degrees from steps ALTITUDE: %s' %(round(deg_alt,3)))
        print('\t Degrees from steps AZIMUTH: %s' %(round(deg_az,3)))


        # if less than 5 degrees altitude
    else:
                                                            print("OFF")
                                                            ser.write("OFF")
    # Sleep for 10 seconds
    time.sleep(10.0)