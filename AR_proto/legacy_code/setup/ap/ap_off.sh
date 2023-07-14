#AP化OFF
#<<実行方法>>
#sudo bash ap_off.sh
echo -e "<<注意>>\n自動的に再起動しちゃいます！！！\nまずい場合は急いで【ctrl+Cで中断】してください"

cd create_ap

#AP化のファイル削除(下2つはap_onでファイル編集したとき使用)
rm -rf /etc/create_ap.conf
rm -rf /etc/network/interfaces
rm -rf /etc/default/hostapd

#stop, disable
sudo systemctl stop create_ap
sudo systemctl disable create_ap

sudo systemctl stop  hostapd
sudo systemctl disable  hostapd

sudo systemctl stop  dnsmasq
sudo systemctl disable  dnsmasq

#sudo reboot AP化オフにするときはrebootまでしないとvnc接続でrebootできなくなっちゃう
sudo reboot