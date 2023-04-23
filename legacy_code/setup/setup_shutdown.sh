#!/bin/sh
#シャットダウンボタンのセットアップ
#Last update 2020/07/25 Hikaru Kimura
#<<実行方法>>
#bash setup_shutdown.sh
#./setup_shutdown.sh
#上記２つのどちらかのコマンドをターミナルに打ち込む
mkdir bin/

sudo cat > ./bin/shutdown_button.py <<EOF
import time
import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        GPIO.wait_for_edge(22, GPIO.FALLING)
        sw_counter = 0

        while True:
            sw_status = GPIO.input(22)

            if sw_status == 0:
                sw_counter = sw_counter + 1
                if sw_counter >= 200: #2秒以上押し続けるとshutdownコマンド実行
                    os.system("sudo shutdown -h now")
                    break
            else:
                break
EOF

sudo cat > /etc/rc.local <<EOF
/home/pi/bin/shutdown_button.py
exit 0
EOF

#serviceファイルの作成
#以下の項目追加
#sudo bash -c "cat >> /lib/systemd/system/shutdown.service" <<EOF
#[Unit]
#Description = shutdown

#[Service]
#ExecStart=/usr/bin/python3 /home/pi/shutdown.py
#Restart=always
#Type=simple

#[Install]
#WantedBy=multi-user.target
#EOF

#ラズパイ起動時にサービスを自動起動
#sudo systemctl enable shutdown.service

#実行権限を与える
#sudo chmod +x setup_shutdown.sh

#設定完了の喜びの舞
echo -e "<<設定完了のおしらせ>>\nおめでとう！設定完了だ！あとでrebootしてね。"
