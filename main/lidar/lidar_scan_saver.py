#!/usr/bin/env python3
from rplidar import RPLidar
import json
import time

PORT_NAME = 'COM3'


def run(path):
    '''Main function'''
    lidar = RPLidar(PORT_NAME)
    data = []
    try:
        print('Recording measurments... Press Crl+C to stop.')
        for scan in lidar.iter_scans():
            data.append([time.time(),scan])
    except KeyboardInterrupt:
        print('Stoping.')
    lidar.stop()
    lidar.disconnect()
    with open("datav2.txt", "w") as fp:
        json.dump(data,fp)

if __name__ == '__main__':
    path = "C:\\Users/hugue/Documents/projet_transversal/datav2.txt"
    run(path)