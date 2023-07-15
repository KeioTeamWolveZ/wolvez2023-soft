#Last Update 2023/06/20
#Author : Masato Inoue


import RPi.GPIO as GPIO
from cansat import Cansat
import time

"""
ステート説明

0. preparing()        準備ステート．センサ系の準備．一定時間以上経過したらステート移行．
1. flying()           放出準備ステート．フライトピンが接続されている状態（＝ボイド缶に収納されている）．フライトピンが外れたらステート移行．
2. droping()          降下&着陸判定ステート．加速度センサの値が一定値以下の状態が一定時間続いたら着陸と判定しステート移行．
3. landing()          分離ステート．分離シートの焼ききりによる分離，モータ回転による分離シートからの離脱を行ったらステート移行．
4. first_releasing()  電池モジュール放出ステート．モジュール放出のための焼き切りのあと，二つ目のモジュール放出のために一定時間走行したらステート移行．
5. second_releasing() 電力消費モジュール放出ステート．モジュール放出のための焼き切りのあと，右旋回をおこなってモジュールを横からみられる位置に移動したらステート移行．
6. connecting()       モジュール接続ステート．電池モジュールに接近・把持を行った後，電力消費モジュールに接近・接続を行い，接続を確認してステート移行．
7. running()          ランバックステート．能代大会ミッション部門では使用しない．ARLISSにおいて，ゴール地点を目指して走行する．ゴールを判定したら走行を終了してステート移行．
8. finish()           終了ステート．

"""

start_state = 4  
end_state = 5

cansat = Cansat(start_state)
cansat.setup()

try:
    while True:
        cansat.sensor()
        time.sleep(0.03)
        cansat.sequence()
        if cansat.state > end_state:
            print("Finished")
            cansat.keyboardinterrupt()
            GPIO.cleanup()
            break
    
except KeyboardInterrupt:
    print("Finished")
    cansat.keyboardinterrupt()
    time.sleep(1)
    GPIO.cleanup()
    time.sleep(1)
    GPIO.cleanup() 
