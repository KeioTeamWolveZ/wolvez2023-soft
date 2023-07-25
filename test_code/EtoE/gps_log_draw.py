import numpy as np
import matplotlib.pyplot as plt
import sys

def gpslogger(start_time):
    filename = f'results/{start_time}/control_result.txt'
    try:
        with open(filename, "r") as f:
            lines = f.read().split(',')
    except FileNotFoundError:
        print(f"指定したファイルがありません．確認してください．\nファイル名 : {filename}")
        sys.exit()

    Lat = [round(float(s[4:]),4) for s in lines if 'Lat' in s]
    Lng = [round(float(s[4:]),4) for s in lines if 'Lng' in s]
    time = [s[5:] for s in lines if 'Time' in s]
    
    plt.figure()
    plt.plot(Lng,Lat)
    plt.xlabel("Lng")
    plt.ylabel("Lon")
    plt.title("GPS log: "+start_time)
    plt.show()
    
if __name__ == '__main__':
    arg = sys.argv
    if len(arg) < 2:
        starttime = input("input start time: ")
    else:
        starttime = arg[1]
    gpslogger(starttime)