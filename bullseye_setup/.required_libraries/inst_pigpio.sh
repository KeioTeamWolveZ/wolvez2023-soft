#!/bin/bash
#pigpioのsetting file
#Last update 2023/07/16 Masato Inoue


sudo systemctl enable pigpiod
sudo systemctl start pigpiod

#設定完了の舞
echo -e "<<設定完了のお知らせ>>\pigpiod has been turnd on successfully"
