# 全てのモジュールのインストール
# Latest update / 2023-04-28 Masato Inoue

echo -e "<<CAUTION!!!!>>\nThis device will be rebooted soon\nOr CTRL+C for cancel\n\n"

## system
sudo bash .setup_sys/setup_sys.sh

## libcamera
sudo bash .camera/inst_libcamera.sh

## Opencvのインストール
sudo bash .camera/inst_opencv_2023.sh

## Matplotlibのインストール
sudo bash .required_libraries/inst_matplotlib.sh
mv libcamera0_0.git20230321+74d023d8-1_armhf.deb .camera/
mv libcamera-apps_0.git20230309+4def288-1_armhf.deb .camera/
mv libcamera-dev_0.git20230321+74d023d8-1_armhf.deb .camera/
mv libcamera_apps_links.txt .camera/
mv libcamera_links.txt .camera/
mv packages.txt .camera/
mv install_pivariety_pkgs.sh .camera/

## sensors
### gps
bash .sensors/setup_gps.sh

### i2c
bash .sensors/setup_i2c.sh

# Apply all settings
sudo reboot

## 体験型コンテンツ用のインストール
#pip3 install keyboard
#pip3 install pytk
