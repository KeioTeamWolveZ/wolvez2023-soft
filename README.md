# wolvez2022
Mission code in Python for Keio Wolve'Z CanSat project 2022

## Hardware Requirements
- Microcomputer
  - Raspberry Pi 4B
  <div align="left">
  <img src="https://user-images.githubusercontent.com/57528969/90947202-008d8980-e46f-11ea-964d-d67bf354345d.png" width="20%" title="Raspberry Pi 3B">
  </div>
- Sensors
    
    |**Sensor**|**Products**|**image**|
    |:---:|:---:|:---:|
    |Camera|[Raspberry Pi Camera Module V2](http://akizukidenshi.com/catalog/g/gM-10518/)|<img src="https://user-images.githubusercontent.com/57528969/91016338-95d37e00-e627-11ea-8958-fba777a15778.png" width="20%" title="Raspberry Pi Camera Module V2">|
    |Communication Module|[ES920LR](https://easel5.com/products/es920lr/)|<img src="https://user-images.githubusercontent.com/57528969/90114355-92b9d180-dd8d-11ea-8565-76540eea0920.png" width="20%" title="Communication Module">|
    |GPS module|[GYSFDMAXB](http://akizukidenshi.com/catalog/g/gK-09991/)|<img src="https://user-images.githubusercontent.com/57528969/90114335-89c90000-dd8d-11ea-82d3-70ab748fa5f2.png" width="20%" title="GPS Module">|
    |Accelaration Sensor|[BNO055](https://www.switch-science.com/catalog/5511/)|<img src="https://user-images.githubusercontent.com/57528969/90114534-ce549b80-dd8d-11ea-81fd-3569fe0b1477.png" width="20%" title="Accelaration Sensor">|
    |Motor|[75:1 Metal Gearmotor 25Dx69L mm HP 6V with 48 CPR Encoder](https://www.pololu.com/product/4806)|<img src="https://a.pololu-files.com/picture/0J9890.600x480.jpg?c6dfea6448bb8ef0cef701de2d59b4d6" width="20%" title="Motor">|
    |Motor Driver|[TB6612FNG](https://toshiba.semicon-storage.com/jp/semiconductor/product/motor-driver-ics/brushed-dc-motor-driver-ics/detail.TB6612FNG.html)|<img src= "https://user-images.githubusercontent.com/63459574/114264109-faf7aa80-9a23-11eb-8417-c08905610e5e.png" width="20%" title="Motor Driver">|

## Software Requirements
Firstly, you need to clone this repository
```
git clone git@github.com:Toshiki-Keio/wolvez2022.git
```
### Setups
**1. OpenCV**  
  OpenCV is necessary for implimenting image processing in order to recognize following target. <br>
  Go to `setup` folder and run `inst_opencv.sh` to install opencv.
```
 sudo bash inst_opencv.sh
```
  Check in python if you successflly installed opencv or not 
```Python
 import cv2
```

**2. GPS Setup**  
  The proposed robot orients itself by GPS. Run `setup_gps.sh`  in terminal. (in `setup` folder)
  
```
sudo bash setup_gps.sh
```

**3. I2C Setup**  
I2C is one of the ways of serial communication. This is necessary for BNO055 (acceralation sensor). Run `setup_i2c` in terminal. (in `setup` folder)

```
sudo bash setup_i2c.sh
```

**4. Install Libraries**<br>
If you want to run mission code, run `Testcode/EtoE/main.py`.<br>
However, you need to install some libraries to run this code without any error. <br>
Run `requirements.sh` in terminal. (in  `setup` folder)

```
sudo bash requirements.sh
```

**5. Access Point Setup (Additional)**  
  if you want to use Raspberry Pi remotely in **No Wi-fi** environment, you may want to use your Rasberry Pi as Wi-fi access point. Then go to `setup/ap` and run `setup_ap.sh`
  
```
sudo bash setup_ap.sh
```
  
  Once you activate access point, you cannot connect your Raspberry Pi to other Wi-fi networks. So you can turn it off by running `ap_off.sh`.
  If you want to re-activate, then, run  `ap_on.sh`

## Project Member
- Project manager   
  Mitsuhiro Takahashi
- Software (★: Part leader)  
  ★Toshiki Fukui, Takafumi Fujii, Masato Inoue, Kazuyuki Hayashide
- Hardware (★: Part leader)  
  ★Moeka Yoshinari, Miyu Konishi, Arisa Shindo, Shingo Murayama
- Circuit (★: Part leader)  
  ★Toshiki Fukui, Shingo Murayama

