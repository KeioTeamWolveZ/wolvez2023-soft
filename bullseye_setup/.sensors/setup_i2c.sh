#!/bin/bash
#i2c通信のセットアップ
#last update 2020/07/08 Yuji Tanaka
#<<実行方法>>
#bash setup_i2c.sh
#./setup_i2c.sh
#上記２つのどちらかのコマンドをターミナルに打ち込む

#moduleファイルに以下の項目を追加
sudo bash -c "cat >> /etc/modules" << EOF
i2c-bcn2708
i2c-dev
EOF

#update
sudo apt-get update -qq

#i2cのtoolをインストール
#sudo apt-get install -y python-smbus i2c-tools -qq
sudo pip3 install smbus
#設定完了の喜びの舞
echo -e "<<設定完了のおしらせ>>\nsmbus has been installed successfully"

#reboot after 10s
#sudo shutdown -r +10

