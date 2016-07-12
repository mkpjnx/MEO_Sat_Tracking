import serial
import time

class GPS:
    '''Provides access to a GPS unit through a serial port'''
    ''' ----> Set GPS to ouput GPRMC lines only <---- '''
    '''Call refresh() function after every sampling iteration to update information'''
    
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud)
        
        time.sleep(5)
        self.ser.flushInput() #Clear out initial junk lines
        
        self.info = str(self.ser.readline())[2:].split(',')

    def refresh(self): #Read most recent line sent by GPS into a list
        #Call this function after every sampling iteration
        self.info = str(self.ser.readline())[2:].split(',')

    def isFixed(self): #Check fix state of GPS and return True/False
        try:
            self.info.index('A')
            return True

        except ValueError:
            return False
    
    def getLat(self): #Return latitude in degrees as a float
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

    def getLon(self): #Return longitude in degrees as a float
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
    
    def getTime(self): #Return current time (in UTC (!!!)) as a formatted string
        try:
            if len(self.info[1]) == 10:
                time_str = self.info[1] 
                return time_str[0:2] + ':' + time_str[2:4] + ':' + time_str[4:] #Format time to HH:MM:SS.SSS

            else:
                return None
            
        except IndexError:
            return None

    def getDate(self): #Return date of latest fix as a formatted string
        try:
            if len(self.info[9]) == 6:
                date_str = self.info[9]
                return date_str[0:2] + '/' + date_str[2:4] + '/' + date_str[4:] #Format date to DD/MM/YY

            else:
                return None

        except IndexError:
            return None

    def getSpeed(self): #Return speed in knots as a float, calculated differentially by the GPS unit
        try:
            return float(self.info[7])
        
        except IndexError:
            return None

    def getBearing(self): #Return bearing in degres as a float*
        #*GPS actually returns 'Course made good', which is really the direction of its movement, and does not necessarily translate to bearing
        try:
            return float(self.info[8])

        except IndexError:
            return None

    def getMagneticVariation(self): #Return magnetic variation at location (not exactly sure what these means/how accurate)
        #Add this variation to your magnetic bearing to get true bearing     
        try:
            if self.info[11] == 'E':
                return -float(self.info[10])

            elif self.info[11] == 'W':
                return float(self.info[10])

            else:
                return None

        except IndexError:
            return None
        
