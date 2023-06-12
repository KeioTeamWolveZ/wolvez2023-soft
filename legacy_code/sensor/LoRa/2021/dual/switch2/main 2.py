# -*- coding: utf-8 -*-
import sys

import lora_send
import lora_recv
import lora_swit


def main(argc, argv):
    #lora_device = "/dev/ttyS0"  # ES920LRデバイス名
    lora_device = "/dev/ttyAMA1" # ES920LRデバイス名
    if argc < 2:
        print('Usage: python %s [send | recv | swit]' % (argv[0]))
        print('       [send | recv | switch] ... mode select')
        sys.exit()
    if argv[1] != 'send' and argv[1] != 'recv' and argv[1] != 'swit':
        print('Usage: python %s [send | recv| swit]' % (argv[0]))
        print('       [send | recv| swit] ... mode select')
        sys.exit()

#     # チャンネル番号を入力
#      channel = input('channel:')
    channel=15

    # 送信側の場合
    if argv[1] == 'send':
        lr_send = lora_send.LoraSendClass(lora_device, channel)
        lr_send.lora_send()
    # 受信側の場合
    elif argv[1] == 'recv':
        lr_recv = lora_recv.LoraRecvClass(lora_device, channel)
        lr_recv.lora_recv()

    elif argv[1] == 'swit':
        lr_swit = lora_swit.LoraSwitClass(lora_device, channel)
        lr_swit.lora_swit()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
    sys.exit()

