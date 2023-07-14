import time
import gps

class cansat(object):
    def __init__(self):
        self.gps = gps.GPS()

    def setup(self):
        self.gps.setupGps()
        
    def writeData(self):
        self.gps.gpsread()
        timer = 1000*(time.time() - start_time)
        timer = int(timer)
        datalog = str(timer) + ","\
                  + "Time:" + str(self.gps.Time) + ","\
                  + "緯度:" + str(self.gps.Lat) + ","\
                  + "経度:" + str(self.gps.Lon)
        print(datalog)
    
    '''
        with open("test.txt",mode = 'a') as test:
            test.write(datalog + '\n')
'''

start_time = time.time()
cansat = cansat() 
cansat.setup()
while True:
    cansat.writeData()
    time.sleep(1)