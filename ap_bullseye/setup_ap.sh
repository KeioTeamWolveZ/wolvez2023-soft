# installation of hostapd and dnsmasq
sudo apt install hostapd dnsmasq

# edit dhcpcd.conf
sudo sed -i "$ a interface=wlan0" /etc/dhcpcd.conf
sudo sed -i "$ a static ip_address=192.168.249.1/24" /etc/dhcpcd.conf

# create /etc/hostapd/hostapd.conf
# EDIT; ssid and wpa_passphrase
sudo cat > /etc/hostapd/hostapd.conf <<EOF
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=wlan0
driver=nl80211
ssid=wolvez2023_1
hw_mode=g
country_code=JP
channel=11
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=wolvez2023
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# edit /etc/default/hostapd
sudo sed '/DEAMON_CONF=/c/ DAEMON_CONF="/etc/hostapd/hostapd.conf"' /etc/default/hostapd

# turn on the survice
sudo systemctl unmask hostapd.service
sudo systemctl enable hostapd.service

# how to check start and stop the service
# sudo systemctl start hostapd.service
# sudo systemctl stop hostapd.service

# comment out network information
sudo sed '4,$s/^/# /g' /etc/wpa_supplicant/wpa_supplicant.conf

# turn on ap setting
sudo rfkill unblock wifi

# reboot
sudo reboot