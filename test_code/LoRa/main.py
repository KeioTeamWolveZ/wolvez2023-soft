from lora import lora
import time


def sendLoRa(lr): #通信モジュールの送信を行う関数
	datalog = "Test-state" + ","\
			  + f"{time.time():.1f}" + ","\
			  + "latitude" + ","\
			  + "longitude"

	lr.sendData(datalog) #データを送信

if __name__ == "__main__":
	lr = lora()
	while True:
		try:
			sendLoRa(lr)
		except KeyboardInterrupt:
			break
