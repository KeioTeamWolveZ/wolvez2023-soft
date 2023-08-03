from lora import lora
import time


def sendLoRa(lr): #通信モジュールの送信を行う関数
	datalog = f"Channel change exam {time.time():.1f}"
	lr.sendData(datalog) #データを送信

if __name__ == "__main__":
	lr = lora()
	while True:
		try:
			sendLoRa(lr)
			time.sleep(3)
		except KeyboardInterrupt:
			break
