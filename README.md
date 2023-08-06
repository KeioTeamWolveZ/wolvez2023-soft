# wolvez2023
Mission code in Python for Keio Wolve'Z CanSat project 2023

## Hardware Requirements
- Microcomputer
  - [Raspberry Pi 4B](https://www.iodata.jp/product/pc/raspberrypi/ud-rp4b/spec.htm)
  <div align="left">
  <img src="https://www.iodata.jp/product/pc/raspberrypi/ud-rp4b/640/m.jpg" width="50%" title="Raspberry Pi 3B">
  </div>
- Sensors
    
    |**Sensor**|**Products**|**image**|
    |:---:|:---:|:---:|
    |Camera|[High resolution Auto-Focus-Camera for Raspberry Pi](https://www.switch-science.com/products/7681)|<img src="https://www.switch-science.com/cdn/shop/products/fd232008-dcf5-4002-9068-5b61865480b0_9df2ed2d-08cc-4924-a8a1-8da612fa3c71_700x700.jpg?v=1687511163" width="20%" title="High resolution Auto-Focus-Camera for Raspberry Pi">|
    |Communication Module|[ES920LR](https://easel5.com/products/es920lr/)|<img src="https://user-images.githubusercontent.com/57528969/90114355-92b9d180-dd8d-11ea-8565-76540eea0920.png" width="20%" title="Communication Module">|
    |GPS module|[GYSFDMAXB](http://akizukidenshi.com/catalog/g/gK-09991/)|<img src="https://user-images.githubusercontent.com/57528969/90114335-89c90000-dd8d-11ea-82d3-70ab748fa5f2.png" width="20%" title="GPS Module">|
    |Accelaration Sensor|[BNO055](https://www.switch-science.com/catalog/5511/)|<img src="https://user-images.githubusercontent.com/57528969/90114534-ce549b80-dd8d-11ea-81fd-3569fe0b1477.png" width="20%" title="Accelaration Sensor">|
    |Motor|[75:1 Metal Gearmotor 25Dx69L mm HP 6V with 48 CPR Encoder](https://www.pololu.com/product/4806)|<img src="https://a.pololu-files.com/picture/0J9890.600x480.jpg?c6dfea6448bb8ef0cef701de2d59b4d6" width="20%" title="Motor">|
    |Motor Driver|[TB6612FNG](https://toshiba.semicon-storage.com/jp/semiconductor/product/motor-driver-ics/brushed-dc-motor-driver-ics/detail.TB6612FNG.html)|<img src= "https://user-images.githubusercontent.com/63459574/114264109-faf7aa80-9a23-11eb-8417-c08905610e5e.png" width="20%" title="Motor Driver">|

## Software Requirements
Firstly, you need to clone this repository
```
git clone git@github.com:KeioTeamWolvez2023/wolvez2023-soft.git
```
### Setups
**1. Requirements**  
  Some additional libraries and settings in raspi-config are necessary for this project. <br>
  Go to `bullseye_setup` folder and run `requirements.sh` to install libraries and setup some configurations. <br>
  If you want check or change details, go to scripts in each hidden folder; `.camera/`, `.required_libraries/`, `.sensors/`, `.setup_sys/`
```
 sudo bash requirements.sh
```
  Check in python if you successflly installed opencv, pigpio or not 
```Python
 import cv2
 import pigpio
```
  Check in terminal if you successflly installed libcamera or not 
```
 libcamera-hello
```
 Dir tree is bellow
```
 ├─bullseye_setup
 │  ├─.camera
 │  ├─.required_libraries
 │  ├─.sensors
 │  ├─.setup_sys
 │  └─ap
```

**2. Additional Settings**  
  You have to change some configurations after run `requirements.sh`.
  See details in [wiki](https://github.com/KeioTeamWolvez2023/wolvez2023-soft/wiki/%E6%96%B0%E8%A6%8FSD%E3%81%AE%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97%E6%96%B9%E6%B3%95#%E8%A8%AD%E5%AE%9A%E7%94%BB%E9%9D%A2%E3%81%A7%E3%81%AE%E8%A8%AD%E5%AE%9A) for setup.

**3. Run**<br>
  Before run mission code, you may have to install our package `Wolvez2023`. <br>
  Go to folder `EtoE/`, and enter bellow in terminal. <br>
```
  pip install -e ./wolvez2023_pkg/
```
  After all, if you want to run mission code, run `/EtoE/main.py`.<br>


**4. Access Point Setup (When you need to connect with VNC viewer)**  
  if you want to use Raspberry Pi remotely in **No Wi-fi** environment, you may want to use your Rasberry Pi as Wi-fi access point. Then go to `bullseye_setup/ap` and run `setup_ap.sh`
  
```
sudo bash setup_ap.sh
```
  
  Once you activate access point, you cannot connect your Raspberry Pi to other Wi-fi networks. So you can turn it off by running `ap_off.sh`.
  If you want to re-activate, then, run  `ap_on.sh`

## Project Member
- Project manager   
  Hayashide Kzuyuki
- Software (★: Part leader)  
  ★Masato Inoe, Ko Ota, Yuma Suzuki
- Hardware (★: Part leader)  
  ★Shingo Murayama, Arisa Shindo, Yukino Ot, Aine Koyama, Karin Yoshino
- Circuit (★: Part leader)  
  ★Shingo Murayam, Ko Ota