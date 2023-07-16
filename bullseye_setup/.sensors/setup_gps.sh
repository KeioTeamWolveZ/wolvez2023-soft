 #!/bin/bash
#GPSのセットアップ
#Last update 2023-04-28 Masato Inoue
#<<実行方法>>
#bash setup_gps.sh
#./setup_gps.sh
#上記２つのどちらかのコマンドをターミナルに打ち込む

#/boot/cmdline.txtの修正
sudo sed -i "s/console=serial0,115200//g" /boot/cmdline.txt

#Serial Mosuleのインストール
#sudo apt-get install python-serial -qq
sudo pip3 install pyserial
#実行権限を与える
sudo chmod +x /home/wolvez2023/wolvez2023-soft/bullseye_setup/.sensors/setup_gps.sh

#設定完了の喜びの舞
#echo -e "<<設定完了のおしらせ>>\nおめでとう！設定完了だ！君はまだ強くなれる。"
