#RPiのAP化初回セットアップ
#<<実行方法>>
#sudo bash setup_ap.sh

#参考
#https://kokensha.xyz/raspberry-pi/raspberry-pi-wifi-access-point/

#１．電通大さんの参考
sudo apt-get install hostapd
sudo apt install dnsmasq iptables

#create_apのインストール
git clone https://github.com/oblique/create_ap
cd create_ap
sudo make install
#create_ap.confの内容書き換え
sudo sed -i -- 's/GATEWAY=10.0.0.1/GATEWAY=10.0.0.3/g' /etc/create_ap.conf
sudo sed -i -- 's/INTERNET_IFACE=eth0/INTERNET_IFACE=lo/g' /etc/create_ap.conf
sudo sed -i -- 's/SSID=MyAccessPoint/SSID=wolvez2020/g' /etc/create_ap.conf
sudo sed -i -- 's/PASSPHRASE=12345678/PASSPHRASE=wolvez2020/g' /etc/create_ap.conf
#ssidとpassphraseは好きなもので！

sudo systemctl enable create_ap
sudo systemctl start create_ap


#２．追加 （参考→http://norikyu.blogspot.com/p/raspberry-pi3-lan-ap.html）

#ファイル編集２つ(network/interfaces, /etc/default/hostapd)
sudo cat > /etc/network/interfaces <<EOF
source-directory /etc/network/interfaces.d
auto lo
iface lo inet loopback
iface eth0 inet manual
auto wlan0
allow-hotplug wlan0
iface wlan0 inet static
EOF

sudo echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'>>/etc/network/interfaces

#dnsmasqのインストール
sudo apt-get install dnsmasq

#reboot 
echo -e "<<設定完了のおしらせ>>\nお疲れ様です！AP化初期設定完了！ 再起動お願いします！"