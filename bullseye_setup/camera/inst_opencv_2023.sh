#!/bin/bash
#Opencv&Numpyのインストールファイル
#Last update 2023/04/13 Harumi Akashi

#ラズパイのパッケージ更新
sudo apt-get update
sudo apt-get upgrade

#pipの更新
sudo pip install --upgrade pip

#OpenCVと依存関係のあるライブラリのインストール
#sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-100 #libhdf5-100のインストールがうまくいかないときは、libhdf5-103
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103 #libhdf5-103のインストールがうまくいかないときは、libhdf5-100
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev

#Opencvnoインストール（あえてバージョンを落としてバグらないようにする）
sudo pip3 --default-timeout=1000 install opencv-python==4.4.0.44
sudo pip3 install opencv-contrib-python==4.4.0.44
#エラーになるときはインストールできるバージョンを探す
#sudo pip3 install opencv-python==

#なんかわかんないけど必要な作業(使った記憶がないが先人の知恵です)
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
sudo echo "export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1">>~/.bashrc

#設定完了の舞
echo -e "<<設定完了のお知らせ>>\nよくやった！！これで設定は終わりだ！"
