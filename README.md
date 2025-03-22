# Updates display on Epomaker RT100 connected with 2.4 dongle

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
  --cpu CPU             Cpu load, will be clipped to [0, 99]
  --current-cpu         Show current CPU load
  --temperature TEMPERATURE
                        Temperature, will be clipped to [-99, 127]
  --current-temperature
                        Show current CPU temperature
  --time TIME           Time in iso format (1111-11-11T11:11)
  --current-time        Show current time
  --monitor MONITOR     Update all values every n seconds
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