# Setting in systemctl
# Last update: 2023/7/19 Masato Inoue


# turn pins off
cp ./turn_off_pins.py /home/wolvez2023/Desktop/
touch /etc/systemd/system/pin_off.service

sudo cat > /etc/systemd/system/pin_off.service <<EOF
[Unit]
Description=Do test

[Service]
ExecStart=/usr/bin/python3 /home/wolvez2023/Desktop/turn_off_pins.py

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable pin_off.service
sudo systemctl start pin_off.service

# turn on pigpiod
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

echo -e "Turned on pin off service"
