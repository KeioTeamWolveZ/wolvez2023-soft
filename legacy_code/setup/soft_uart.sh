#RPiのAP化初回セットアップ
#<<実行方法>>
#sudo bash soft_uart.sh

cd /home/pi/Desktop/wolvez2021/sensor/GPS
git clone https://github.com/adrianomarto/soft_uart
sudo apt-get install raspberrypi-kernel-headers
cd soft_uart
make
sudo make install
sudo insmod soft_uart.ko
sudo insmod soft_uart.ko gpio_tx=23 gpio_rx=24
