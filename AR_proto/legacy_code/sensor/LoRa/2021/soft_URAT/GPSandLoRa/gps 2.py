import serial
import micropyGPS
import time
import threading

class GPS(object):        
    
    def __init__(self):
        self.mgps = micropyGPS.MicropyGPS(9,'dd') 
        self.Time = 0
        self.Lat = 0
        self.Lon = 0
        #self.gps_device = "dev/serial0"  # ES920LRデバイス名
        
        
    def rungps(self): # GPSモジュールを読み、GPSオブジェクトを更新する
        s = serial.Serial('/dev/ttyAMA0', 9600, timeout=10)
        s.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
        while True:
            sentence = s.readline().decode('utf-8') # GPSデーターを読み、文字列に変換する
            if sentence[0] != '$': # 先頭が'$'でなければ捨てる
                continue
            for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
                self.mgps.update(x)

    def setupGps(self):
        gpsthread = threading.Thread(target=self.rungps, args=()) # 上の関数を実行するスレッドを生成
        gpsthread.daemon = True
        gpsthread.start() # スレッドを起動

    def gpsread(self):
        #while True:
        if self.mgps.clean_sentences > 20: # ちゃんとしたデーターがある程度たまったら出力する
             h = str('%02d' % (self.mgps.timestamp[0])) if self.mgps.timestamp[0] < 24 else self.mgps.timestamp[0] - 24
             m = str('%02d' % (self.mgps.timestamp[1]))
             s = str('%02d' % (self.mgps.timestamp[2]))
             self.Time = h + ":" + m + ":" + s
         
             self.Lat = str('%2.8f' % (self.mgps.latitude[0]))
             self.Lon = str('%2.8f' % (self.mgps.longitude[0]))
 
             #print('時間：', self.Time, ",", end='')     #main.pyで格納を確認するため、最後は消す
             #print('緯度：', self.Lat, ",", end='')
             #print('経度：', self.Lon)
        #time.sleep(1.0) #ここ変える
#g = GPS()
"""
GPS = GPS()
GPS.setupGPS()
while True:
    GPS.gpsread()
    """