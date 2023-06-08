#!/bin/bash
rev=$(cat /proc/cpuinfo | grep Revision | awk '{print substr($NF,length($NF)-5,6)}')
code_name=$(awk -F"[)(]+" '/VERSION=/ {print $2}' /etc/os-release)
kernel_info=$(uname -a)
VERSION=$(uname -r | cut -d - -f 1)
kernel=$(uname -r)
arch=$(arch)
pkg_version=$code_name
rpi_kernel=$(dpkg-query -f '${Version}' --show raspberrypi-kernel)

$(dpkg-architecture -earm64)
if [ $? == 0 ]; then
    pkg_version=$pkg_version"-arm64"
fi

$(dpkg --compare-versions 1:1.20211201~ '>=' $rpi_kernel)
if [[ $? == 1 && $code_name != "buster" ]]; then
    pkg_version=$pkg_version"-v5"
fi

echo "================================================="
echo "Hardware Revision: ${rev}"
echo "Kernel Version: ${kernel}"
echo "OS Codename: ${code_name}"
echo "ARCH: ${arch}"
echo "================================================="
echo ""

CONFIG_FILE_NAME=packages.txt
CONFIG_FILE_DOWNLOAD_LINK=https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/packages.txt
RED='\033[0;31m'
NC='\033[0m' # No Color

updatePackages()
{
    rm -f $CONFIG_FILE_NAME
    wget -O $CONFIG_FILE_NAME $CONFIG_FILE_DOWNLOAD_LINK
    source $CONFIG_FILE_NAME
}

listPackages()
{
    if [ ! -f $CONFIG_FILE_NAME ]; then
        updatePackages
    fi
    source $CONFIG_FILE_NAME
    echo "Supported packages:"
    for key in ${!package_cfg_names[*]};do
    echo -e "\t$key"
    done
    echo ""
}

helpFunction()
{
    if [ ! -f $CONFIG_FILE_NAME ]; then
        updatePackages
    fi
    echo ""
    echo "Usage: $0 [option]... -p <package name>"
    echo -e "Options:"
    echo -e "\t-p <package name>\tSpecify the package name."
    echo -e "\t-h \t\t\tShow this information."
    echo -e "\t-l \t\t\tAuto detect camera and install the corresponding driver."
    echo -e "\t-l \t\t\tUpdate and list available packages."
    echo ""
    listPackages
    exit 1
}

initAutodetect() {
    array=()
    arr_subscript=0
    InstallName=
    SenorId=
    OpenCameraName=
    BOOTCONFIG="/boot/config.txt"
    BIT=`getconf LONG_BIT`
    # PWD_GET=`pwd`
    PrintCamera=
}

removeDtoverlay() {
    sudo dtoverlay -r imx519>/dev/null 2>&1
    sudo dtoverlay -r arducam>/dev/null 2>&1
    sudo dtoverlay -r arducam-pivariety>/dev/null 2>&1
    sudo dtoverlay -r arducam_64mp>/dev/null 2>&1
    sudo dtoverlay -r arducam-64mp>/dev/null 2>&1
}

configCheck() {

    grepcmd i2cdetect
    if [ $? -ne 0 ]; then
        echo "Download i2c-tools."
        sudo apt install -y i2c-tools
    fi
    
    if ! grep -q "^i2c[-_]dev" /etc/modules; then
        sudo printf "i2c-dev\n" >>/etc/modules
        sudo modprobe i2c-dev
    fi
    

    if [ $(grep -c "dtparam=i2c_vc=on" "$BOOTCONFIG") -eq 0 ]; then
        sudo sed -i '$adtparam=i2c_vc=on' "$BOOTCONFIG"
        sudo sed -i '$adtparam=i2c_arm=on' "$BOOTCONFIG"
        echo "Already add 'dtparam=i2c_vc=on' and 'dtparam=i2c_arm=on' in /boot/config.txt"
        sudo dtparam i2c_vc
        sudo dtparam i2c_arm
    fi
    if [[ $(grep -c "^dtoverlay=imx519" "$BOOTCONFIG") -ne 0 \
    || $(grep -c "^dtoverlay=arducam" "$BOOTCONFIG") -ne 0 ]]; then
        echo "You have installed our driver and it works."
        echo "If you want to redetect the camera, you need to modify the /boot/config.txt file and reboot."
        echo "Do you agree to modify the file?(y/n):"
        read USER_INPUT
        case $USER_INPUT in
        'y'|'Y')
            echo "Changed"
            sudo sed 's/^\s*dtoverlay=imx519/#dtoverlay=imx519/g' -i $BOOTCONFIG
            sudo sed 's/^\s*dtoverlay=arducam/#dtoverlay=arducam/g' -i $BOOTCONFIG
            sudo sed 's/^\s*dtoverlay=arducam_64mp/#dtoverlay=arducam_64mp/g' -i $BOOTCONFIG
            
            echo "reboot now?(y/n):"
            read USER_INPUT
            case $USER_INPUT in
            'y'|'Y')
                echo "reboot"
                sudo reboot
            ;;
            *)
                echo "cancel"
                echo "Re-execution of the script will only take effect after restarting."
                exit -1
            ;;
            esac

        ;;
        *)
            echo "cancel"
            exit -1
        ;;
        esac

    fi
}

installFile() {
    
    CAMERA_I2C_FILE_NAME="camera_i2c"
    CAMERA_I2C_FILE_DOWNLOAD_LINK="https://raw.githubusercontent.com/ArduCAM/MIPI_Camera/master/RPI/utils/camera_i2c"
    RPI3_GPIOVIRTBUF_FILE_NAME="rpi3-gpiovirtbuf"

    if [ ! -s $CAMERA_I2C_FILE_NAME ]; then
        wget -O $CAMERA_I2C_FILE_NAME $CAMERA_I2C_FILE_DOWNLOAD_LINK
        chmod +x $CAMERA_I2C_FILE_NAME
    fi
    if [ $? -ne 0 ]; then
        echo -e "${RED}Download failed.${NC}"
        echo "Please check your network and try again."
        exit -1
    fi

    if [ "$BIT" = 32 ]; then
        RPI3_GPIOVIRTBUF_FILE_DOWNLOAD_LINK="https://github.com/ArduCAM/MIPI_Camera/raw/master/RPI/utils/rpi3-gpiovirtbuf/32/rpi3-gpiovirtbuf"
    elif [ "$BIT" = 64 ]; then
        RPI3_GPIOVIRTBUF_FILE_DOWNLOAD_LINK="https://github.com/ArduCAM/MIPI_Camera/raw/master/RPI/utils/rpi3-gpiovirtbuf/64/rpi3-gpiovirtbuf"
    fi

    if [ ! -s $RPI3_GPIOVIRTBUF_FILE_NAME ]; then
        wget -O $RPI3_GPIOVIRTBUF_FILE_NAME $RPI3_GPIOVIRTBUF_FILE_DOWNLOAD_LINK
    fi

    if [ $? -ne 0 ]; then
        echo -e "${RED}Download failed.${NC}"
        echo "Please check your network and try again."
        exit -1
    else
        chmod +x $RPI3_GPIOVIRTBUF_FILE_NAME
        ./camera_i2c>/dev/null 2>&1
    fi
}

grepcmd() {
    type $1 >/dev/null 2>&1 || {
        echo >&2 "Start install $1."
        return 1
    }
}

judgeI2c() {
    for element in ${array[@]}; do
        if [ "$1" = "$element" ]; then
            return 0
        fi
    done
    return 1
}

judgeSenorId() {
    if [ "$1" = "0c" ]; then
        i2ctransfer -y 10 w2@0x0c 0x01 0x03 r4
    elif [ "$1" = "1a" ]; then
        i2ctransfer -y 10 w2@0x1a 0x00 0x16 r2
    elif [ "$1" = "50" ]; then
    	i2ctransfer -y 10 w2@0x50 0x00 0x5E r2
    fi
}

camera() {
    while read lines; do
        for line in $lines; do
            case "$line" in
            [0-9a-zA-z][0-9a-zA-Z])
                array[arr_subscript]=$line
                let arr_subscript++
                ;;
            esac
        done
    done <$1

    judgeI2c 1a
    if [ $? -eq 0 ]; then
        SenorId=$(judgeSenorId 1a 2>&1)
        if [ "$SenorId" = "0x05 0x19" ]; then
            InstallName="imx519_kernel_driver_low_speed"
            OpenCameraName="imx519"
            PrintCamera="IMX519"
            echo "Recognize that your camera is IMX519."
        fi

    fi

    if [ -z "$InstallName" ]; then

        SenorId=$(judgeSenorId 0c 2>&1)
        
        judgeI2c 0c
        if [ $? -eq 0 ]; then
            if [ "$SenorId" = "0x00 0x00 0x00 0x30" ]; then
                InstallName="kernel_driver"
                OpenCameraName="arducam"
                PrintCamera="Pirvarty"
                echo "Recognize that your camera is Pirvarty"
            fi
        fi
    fi
    
    if [ -z "$InstallName" ]; then

        SenorId=$(judgeSenorId 50 2>&1)
        
        judgeI2c 50
        if [ $? -eq 0 ]; then
            if [ "$SenorId" = "0x41 0x36" ]; then
	    	InstallName="64mp_pi_hawk_eye_kernel_driver"
	    	OpenCameraName="arducam_64mp"
	    	PrintCamera="64MP"
	    	echo "Recognize that your camera is 64MP."
            fi
        fi
    fi

    if [ -z "$InstallName" ]; then
        echo "Your camera does not need to install drivers."
        exit -1
    fi
}


openCamera() {
    if [ -n "$OpenCameraName" ]; then
        sudo dtoverlay $OpenCameraName>/dev/null 2>&1
    fi
}

verlte() {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

while getopts hldv:p: flag
do
    case "${flag}" in
        v)  pkg_version=${OPTARG};;
        p)  package=${OPTARG};;
        d)  initAutodetect
            # removeDtoverlay
            configCheck
            installFile
            i2cdetect -y 10 > i2c.txt
            camera i2c.txt
            package=${InstallName}
            ;;
        l)  updatePackages
            listPackages
            exit 1
            ;;
        ?)  helpFunction;;
    esac
done

if [ ! -f $CONFIG_FILE_NAME ]; then
    updatePackages
fi

source $CONFIG_FILE_NAME

if [ -z $package ]; then
    helpFunction
fi

echo "kernel:$kernel"

package_cfg_name=${package_cfg_names[$package]}

if [[ $package == *"libcamera"* ]]; then
    if [[ $package == *"apps"* ]]; then
        verlte '5.15.30' $VERSION
        if [ $? == 0 ]; then
            package='libcamera_apps_new'
        else 
            package='libcamera_apps'
        fi
        package_cfg_download_link=${package_cfg_download_links[$package]}
    else
        verlte '5.15.30' $VERSION
        if [ $? == 0 ]; then
            package='libcamera'
        else 
            package='libcamera_dev'
        fi
        package_cfg_name=${package_cfg_names[$package]}
        package_cfg_download_link=${package_cfg_download_links[$package]}
    fi
else
    package_cfg_download_link=${package_cfg_download_links[$package]}
fi

if [[ (-z $package_cfg_name) || (-z $package_cfg_download_link) ]]; then
    echo -e "${RED}Unsupported package.${NC}"
    echo ""
    listPackages
    exit -1
fi

rm -f $package_cfg_name
wget -O $package_cfg_name $package_cfg_download_link
source $package_cfg_name

download_link=
pkg_name=

if [[ $package == *"kernel_driver"* ]]; then
    download_link=${package_download_links[$kernel]}
    pkg_name=${package_names[$kernel]}
else
    download_link=${package_download_links[$pkg_version]}
    pkg_name=${package_names[$pkg_version]}
fi


if [[ (-z $pkg_name) || (-z $download_link) ]]; then
    echo -e "${RED}"
	echo -e "Cannot find the corresponding package, please send the following information to support@arducam.com"
    echo -e "Hardware Revision: ${rev}"
    echo -e "Kernel Version: ${kernel}"
    echo -e "Package: ${package} -- ${pkg_version}"

    if [[ $package == *"kernel_driver"* ]]; then
        echo -e "You are using an unsupported kernel version, please install the official SD Card image(do not execute rpi-update):"
        echo -e "https://www.raspberrypi.com/software/operating-systems/"
    fi

    echo -e "${NC}"
	exit -1
fi

rm -rf $pkg_name
wget -O $pkg_name $download_link

if [[ ( $? -ne 0) || (! -f "${pkg_name}") ]]; then
	echo -e "${RED}download failed${NC}"
	exit -1
fi

if [[ $package == *"kernel_driver"* ]]; then
    echo "is kernel driver"
    tar -zxvf $pkg_name Release/
    cd Release/
    ./install_driver.sh
    openCamera
    if [ $PrintCamera ]; then 
        echo "Your camera is "$PrintCamera",and the relevant drivers have been installed."
    fi
else
    if [[ $package == *"libcamera_dev"* ]]; then
        echo -e "remove libcamera0"
        echo ""
        sudo apt remove -y libcamera0
    fi
    
    sudo apt update
    if [ $package == 'libcamera' ]; then
        sudo apt remove -y libcamera-dev
        sudo apt install -y python3-libcamera
    fi
    sudo apt --reinstall install -y ./$pkg_name
    if [ $package == 'libcamera' ]; then
        pkg_name=$(echo ${pkg_name/libcamera0/libcamera-dev})
        download_link=$(echo ${download_link/libcamera0/libcamera-dev})
        wget -O $pkg_name $download_link
        sudo apt --reinstall install -y ./$pkg_name
        sudo apt install -y python3-picamera2
    fi
    # if [[ $package == *"libcamera_apps"* && ! -f /usr/lib/arm-linux-gnueabihf/libboost_program_options.so.1.67.0 ]]; then
    #     echo -e "Soft link to libboost_program_options.so"
    #     echo ""
    #     sudo ln -s /usr/lib/arm-linux-gnueabihf/libboost_program_options.so /usr/lib/arm-linux-gnueabihf/libboost_program_options.so.1.67.0
    # fi
fi

if [ $? -ne 0 ]; then
    echo ""
	echo -e "${RED}Unknown error, please send the error message to support@arducam.com${NC}"
	exit -1
fi
