import serial
import micropyGPS
import time
import threading

def rungps(): # GPSモジュールを読み、GPSオブジェクトを更新する
    s = serial.Serial('/dev/serial0', 9600, timeout=10)
    s.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
    while True:
        sentence = s.readline().decode('utf-8') # GPSデーターを読み、文字列に変換する
        if sentence[0] != '$': # 先頭が'$'でなければ捨てる
            continue
        for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
            gps.update(x)

def thread():
    gpsthread = threading.Thread(target=rungps, args=()) # 上の関数を実行するスレッドを生成
    gpsthread.daemon = True
    gpsthread.start() # スレッドを起動

def gpsread():
    while True:
        if gps.clean_sentences > 10: # ちゃんとしたデーターがある程度たまったら出力する
            h = int(gps.timestamp[0])
            print('時刻 {0}:{1}:{2} ,'.format(h, gps.timestamp[1], gps.timestamp[2]),end='')
            print('緯度: %2.3f ,' % (gps.latitude[0]),end='')
            print('経度: %2.3f' % (gps.longitude[0])) 
        time.sleep(1.0) #ここ変える

gps = micropyGPS.MicropyGPS(9,'dd') # MicroGPSオブジェクトを生成する。
                                     # 引数はタイムゾーンの時差と出力フォーマット
thread()
gpsread()