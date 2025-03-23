# Updates display on Epomaker RT100 connected with 2.4ghz dongle

## Every command here must be run as root

## Installation
```
apt install python3 python3-pip libhidapi-dev
pip3 install -r requirements
```

## Usage
```
usage: main.py [-h] [--cpu CPU] [--current-cpu] [--temperature TEMPERATURE] [--current-temperature] [--time TIME] [--current-time] [--monitor MONITOR]

options:
  -h, --help            show this help message and exit
  --cpu CPU             Show custom cpu load, clipped to [0, 99]
  --current-cpu         Show current CPU load
  --temperature TEMPERATURE
                        Show custom temperature, will be clipped to [-99, 127]
  --current-temperature
                        Show current CPU temperature
  --time TIME           Show date and time in iso format (1111-11-11T11:11)
  --current-time        Show current time
  --monitor MONITOR     Update cpu and temperature every MONITOR seconds, time every 24 hours
```

## Service
```
mkdir /root/rt100-wireless-display
cp main.py /root/rt100-wireless-display/
cp rt100-wireless-display.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rt100-wireless-display.service
service rt100-wireless-display start
```