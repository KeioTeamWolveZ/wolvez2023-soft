# pressure_test
#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import spidev
import time
import os

# SPIバスを開く
spi = spidev.SpiDev()
spi.open(0, 0)

# MCP3008から値を読み取るメソッド
# チャンネル番号は0から7まで


def ReadChannel(channel):
    adc = spi.xfer2([1, (8+channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# 得た値を電圧に変換するメソッド
# 指定した桁数で切り捨てる


def ConvertVolts(data, places):
    volts = (data * 5) / float(1023)
    volts = round(volts, places)
    return volts


# センサのチャンネルの宣言
force_channel = 0

# 値を読むのを遅らせる
delay = 0.25

# メインクラス
if __name__ == '__main__':
    try:
        while True:
            data = ReadChannel(force_channel)
            print("A/D Converter: {0}".format(data))
            volts = ConvertVolts(data, 3)
            print("Volts: {0}".format(volts))
            time.sleep(delay)
# 何か入力したら終了
    except KeyboardInterrupt:
        spi.close()
        sys.exit(0)
