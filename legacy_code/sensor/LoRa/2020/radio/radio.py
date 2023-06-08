import time
import radio_setting

# LoRa送信用クラス
class radio(object):

    def __init__(self):
        # ES920LRデバイス名
        self.lora_device = "/dev/ttySOFT0"
        """
        #config設定
        self.channel = 15   #d
        self.panid = '0001' #e
        self.ownid = '0001' #f
        self.dstid = '0000' #g
        """
        
        self.sendDevice = radio_setting.LoraSettingClass(self.lora_device)
        
    def setupRadio(self):
        """
        # LoRa初期化
        self.sendDevice.reset_lora()
        """
        """
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', self.panid, 'f', self.ownid, 'g', self.dstid,
                    'l', '2', 'n', '1', 'p', '1', 'y', 'z']
                    #l:Ack(ON), n:転送モード(Payload), p:受信電波強度, y:show, z:start
        #os.system("sudo insmod soft_uart.ko")#os
                
        # LoRa設定
        self.sendDevice.setup_lora(set_mode)
        """
        # LoRa設定
        self.sendDevice.setup_lora()
        

    # ES920LRデータ送信メソッド
    def sendData(self, datalog):        
        # LoRa(ES920LR)データ送信
        print(datalog)
        self.sendDevice.cmd_lora(datalog)
         