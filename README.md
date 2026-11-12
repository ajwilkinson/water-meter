This is a new approach as the previous one is no longer compatible with current Raspian versions.

# Hardware install
This now used GPIO17 which is physical pin 11. Wire the meter between pin 11 and any ground pin

# Software installation
Clone the git repo into e.g. home directory

Then
```
sudo mkdir -p /opt/water-meter
sudo cp water-meter.py /opt/water-meter/
sudo cp water-meter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now water-meter
journalctl -u water-meter -f
```
