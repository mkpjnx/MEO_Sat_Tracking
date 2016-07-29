from header import *
import tracker as track

def main():
    tracker = track.Tracker('COM3', 115200)

    while True:
        tracker.refresh()
        print(tracker.get_time())
        
        if tracker.is_fixed():
            print('GPS is fixed')
            print('Lat:', tracker.get_lat(), 'Long:', tracker.get_lon())
            print('Yaw:', tracker.get_yaw())

        else:
            print('Fixing GPS')

        print('\n')
            
main()
