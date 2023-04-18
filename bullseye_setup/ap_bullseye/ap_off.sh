# Setting for turning access point mode off
# Latest edit: 2023-04-16 Masato Inoue

# Delete hostapd.conf
sudo rm -rf /etc/hostapd/hostapd.conf

# Delete dnsmasq.conf
sudo sed -i "/interface=wlan0/d/g" /etc/dnsmasq.conf
sudo sed -i "/dhcp-range=192.168.249.50,192.168.249.150,255.255.255.0,12h/d" /etc/dnsmasq.conf

# Delete ip settings
sudo sed -i '/interface=wlan0/d' /etc/dhcpcd.conf
sudo sed -i '/static ip_address=/d' /etc/dhcpcd.conf
sudo sed -i '/DAEMON_CONF=/c #DAEMON_CONF=""' /etc/default/hostapd

# Stop the service
sudo systemctl stop hostapd
sudo systemctl disable hostapd.service

# comment out network information
sudo sed -i '4,$s/# //g' /etc/wpa_supplicant/wpa_supplicant.conf

# Unblock wifi
# sudo rfkill unblock wifi

# Reboot
# sudo reboot
echo -e "<<設定完了のおしらせ>>\nやばいよ！再起動したらVNC入れなくなっちゃくからね！"