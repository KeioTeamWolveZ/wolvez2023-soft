#Last Update 2023/06/13
#Author : Masato Inoue


import RPi.GPIO as GPIO
from cansat import Cansat
import time

"""
ステート説明

0. preparing()  準備ステート。センサ系の準備。一定時間以上経過したらステート移行。
1. flying()     放出準備ステート。フライトピンが接続されている状態（＝ボイド缶に収納されている）。フライトピンが外れたらステート移行。
2. droping()    降下&着陸判定ステート。加速度センサの値が一定値以下の状態が一定時間続いたら着陸と判定しステート移行。
3. landing()    分離ステート。分離シートの焼ききりによる分離、モータ回転による分離シートからの離脱を行ったらステート移行。
4. spm_first()  第1段階スパースモデリングステート。最初に撮影した画像に特徴処理(10種類:RGB,r,g,b,rb,rg,gb,edge,edge enphasis, HSV)を行い、
                それぞれで辞書作成。再構成した際の元画像との差分のヒストグラムから特徴量（6種類: 平均,分散,中央値,最頻値,歪度,尖度）を抽出。
5. spm_second() 第2段階スパースモデリングステート。第一段階で獲得した特徴処理に対する特徴量（1ウィンドウ60個の特徴量、全体で360個の特徴量）から
                重要な特徴量を抽出。危険度の算出まで可能になる。
6. running()    経路計画&走行ステート。ステート5まで獲得したモデルで危険度を逐次算出しながら経路を計画。計画した経路を走行。
7. relearning() 再学習ステート（未実装）。スタックしたら再度学習を行いモデルを更新。
8. finish()     終了ステート

"""

state =  0

cansat = Cansat(state)
cansat.setup()

try:
    while True:
        cansat.sensor()
        time.sleep(0.03)
        cansat.sequence()
        if cansat.state >= 4:
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
