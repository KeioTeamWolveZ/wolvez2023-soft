# Installation of libcamera command for auto-focus camera
# on Bullseye OS 6.1.21 and later
# Latest edit: 2023-04-14 Masato Inoue

# Step 1. Download the bash scripts
wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x install_pivariety_pkgs.sh

# Step 2. Install `libcamera`
./install_pivariety_pkgs.sh -p libcamera

# Step 3. Install libcamera-apps
./install_pivariety_pkgs.sh -p libcamera_apps

# Step 4. Modify .config file
sudo sed -i "$ a dtoverlay=imx519" /boot/config.txt

#Save and reboot.
echo -e "<<設定完了のおしらせ>>\nもしかして天才？再起動したら使えるようになってるらしいよ"