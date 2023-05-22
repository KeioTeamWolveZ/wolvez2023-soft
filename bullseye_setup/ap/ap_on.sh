# Turning this pi on as access point
# Latest edit: 2023-04-19 Masato Inoue

# edit dhcpcd.conf
sudo sed -i "$ a interface wlan0" /etc/dhcpcd.conf
# ip address can be changed here within 192.168.249.1~150
sudo sed -i "$ a static ip_address=192.168.249.1/24" /etc/dhcpcd.conf
sudo sed -i "$ a nohook wpa_supplicant" /etc/dhcpcd.conf

# edit dnsmasq.conf
sudo sed -i "$ a interface=wlan0" /etc/dnsmasq.conf
sudo sed -i "$ a dhcp-range=192.168.249.50,192.168.249.150,255.255.255.0,12h" /etc/dnsmasq.conf

# create /etc/hostapd/hostapd.conf
# EDIT; ssid and wpa_passphrase
sudo cat > /etc/hostapd/hostapd.conf <<EOF
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=wlan0
driver=nl80211

# SSID can be changed here
ssid=wolvez2023_ip1

hw_mode=g
country_code=JP
channel=11
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2

# pass can be changed here
wpa_passphrase=wolvez2023

wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# edit /etc/default/hostapd
sudo sed -i '/DAEMON_CONF=/c DAEMON_CONF="/etc/hostapd/hostapd.conf"' /etc/default/hostapd

# turn on the survice
sudo systemctl unmask hostapd.service
sudo systemctl enable hostapd.service

# how to check start and stop the service
# sudo systemctl start hostapd.service
# sudo systemctl stop hostapd.service

# comment out network information
sudo sed -i '4,$s/^/# /g' /etc/wpa_supplicant/wpa_supplicant.conf

# turn on ap setting
sudo rfkill unblock wifi

# reboot
# sudo reboot
echo -e 
"<<設定完了のおしらせ>>\nもしかして天才？再起動したらwolvez2023_(ipの最後)で見つかるらしい\n接続先：192.168.249.1\nID：wolvez2023\n pass:wolvez2023"
