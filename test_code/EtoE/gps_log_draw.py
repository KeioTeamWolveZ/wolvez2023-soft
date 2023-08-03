import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime as dt
import constant as ct

def gpslogger(start_time):
    filename = f'results/{start_time}/control_result.txt'
    try:
        with open(filename, "r") as f:
            lines = f.read().split(',')
    except FileNotFoundError:
        print(f"指定したファイルがありません．確認してください．\nファイル名 : {filename}")
        sys.exit()

    Lat = [round(float(s[4:]),6) for s in lines if 'Lat' in s]
    Lng = [round(float(s[4:]),6) for s in lines if 'Lng' in s]
    time = [dt.strptime(s[5:], '%H:%M:%S') for s in lines if 'Time' in s]
    print(time[-1]-time[0])
    
    Lat.pop(Lat==0)
    Lng.pop(Lng==0)
    plt.figure()
    plt.plot(Lng,Lat,color='blue')
    plt.scatter(Lng[0],Lat[0],marker='s',s=30,color='black')
    plt.scatter(Lng[-1],Lat[-1],marker='*',s=80,color='red')
    plt.scatter(ct.const.GPS_GOAL_LON,ct.const.GPS_GOAL_LAT,marker='+',s=100,color='green')
    plt.xlabel("Lng")
    plt.ylabel("Lat")
    plt.grid(True)
    plt.axis("equal")
    plt.title("GPS log: " + start_time + "\nTime of working: " + str(time[-1]-time[0]))
    plt.show()
    
if __name__ == '__main__':
    arg = sys.argv
    if len(arg) < 2:
        starttime = input("input start time: ")
    else:
        starttime = arg[1]
    gpslogger(starttime)
