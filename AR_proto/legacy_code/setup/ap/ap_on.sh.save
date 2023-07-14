#AP化ON(２回目以降)　参考→http://norikyu.blogspot.com/p/raspberry-pi3-lan-ap.html
#<<実行方法>>
#sudo bash ap_on.sh
#ファイル編集(3つ)
#1./etc/create_ap.conf
sudo cat > /etc/create_ap.conf <<EOF
CHANNEL=default
GATEWAY=10.0.0.4
WPA_VERSION=2
ETC_HOSTS=0
DHCP_DNS=gateway
NO_DNS=0
NO_DNSMASQ=0
HIDDEN=0
MAC_FILTER=0
MAC_FILTER_ACCEPT=/etc/hostapd/hostapd.accept
ISOLATE_CLIENTS=0
SHARE_METHOD=nat
IEEE80211N=0
IEEE80211AC=0
HT_CAPAB=[HT40+]
VHT_CAPAB=
DRIVER=nl80211
NO_VIRT=0
COUNTRY=
FREQ_BAND=2.4
NEW_MACADDR=
DAEMONIZE=0
NO_HAVEGED=0
WIFI_IFACE=wlan0
INTERNET_IFACE=lo
SSID=wolvez2023_4
PASSPHRASE=wolvez2023
USE_PSK=0
EOF
#ssidとpassphraseは好きなもの!

#2./etc/network/interfaces
sudo cat > /etc/network/interfaces <<EOF
source-directory /etc/network/interfaces.d
auto lo
iface lo inet loopback
iface eth0 inet manual
auto wlan0
allow-hotplug wlan0
iface wlan0 inet static
EOF

#3.
sudo echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'>>/etc/default/hostapd


#enable, start
sudo systemctl enable create_ap
sudo systemctl start create_ap

#create_apとhostapd,dnsmasqを一緒に使うことできないみたい...!
#sudo systemctl enable  hostapd
#sudo systemctl start  hostapd

#sudo systemctl enable  dnsmasq
#sudo systemctl start  dnsmasq

echo -e "<<設定完了のおしらせ>>\nおめでとう！AP化オン設定完了だ！ 再起動お願いします！"
