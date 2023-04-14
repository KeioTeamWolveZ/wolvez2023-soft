# Setting for turning access point mode off
# Latest edit: 2023-04-14 Masato Inoue

# Delete hostapd.conf
rm -rf /etc/hostapd/hostapd.conf
rm -rf /etc/default/hostapd

# Delete ip settings
sudo sed '/interface=wlan0/d' /etc/dhcpcd.conf
sudo sed '/static ip_address=/d' /etc/dhcpcd.conf

# Stop the service
sudo systemctl stop  hostapd
sudo systemctl disable  hostapd.service

# comment out network information
sudo sed -i '4,$s/^# //g' /etc/wpa_supplicant/wpa_supplicant.conf

# Unblock wifi
sudo rfkill unblock wifi

# Reboot
sudo reboot