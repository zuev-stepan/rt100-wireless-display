import sys
import hid
import time
from datetime import datetime, timedelta
import argparse
import psutil
import keyboard


WIRELESS_RT100_VENDOR_ID = 0x3151
WIRELESS_RT100_PRODUCT_ID = 0x4011
RT100_REPORT_SIZE = 128
SLEEP = 0.3


class KeyboardMonitor:
    def __init__(self, update_period):
        self.update_period = update_period
        self.update()
        keyboard.on_press(lambda x: self.update())

    def update(self):
        self.last_active = datetime.now()


class DeviceHolder(hid.device):
    def __init__(self, vendor_id, product_id, report_size):
        super().__init__()
        device_list = hid.enumerate(vendor_id, product_id)
        device_path = next(t for t in device_list if t['interface_number'] == 1)['path']
        self.open_path(device_path)
        self.set_nonblocking(True)
        self.report_size = report_size

    def send_report(self, hex_str):
        report_bytes = bytearray.fromhex(hex_str)
        if len(report_bytes) > self.report_size:
            raise Exception('Report is too large')
        self.send_feature_report(list(report_bytes) + [0] * (self.report_size - len(report_bytes)))

    def get_report(self):
        self.get_feature_report(0, self.report_size)

    def __del__(self):
        self.close()


class WirelessRT100(DeviceHolder):
    def __init__(self):
        super().__init__(WIRELESS_RT100_VENDOR_ID, WIRELESS_RT100_PRODUCT_ID, RT100_REPORT_SIZE)
        self.poll()
        self.send_report("fe 40")
        self.send_report("f6 0a")
        self.poll()
        self.next_update_time = None

    def poll(self):
        time.sleep(SLEEP)
        self.send_report("f7")
        time.sleep(0.05)
        self.get_report()
        time.sleep(SLEEP)

    def set_cpu(self, value: int):
        value = max(0, value)
        value = min(99, value)

        self.send_report(f"22 00 00 00 00 00 00 dd ab 07 8e 19 06 00 20 00 {value:02x}")
        self.poll()

    def set_temp(self, value: int):
        value = max(-99, value)
        value = min(127, value)
        value = 256 + value if value < 0 else value

        self.send_report(f"2a 00 00 00 00 00 00 d5 {value:02x}")
        self.poll()

    def set_time(self, value: str):
        value = datetime.now() if value == 'NOW' else datetime.fromisoformat(value)
        if self.next_update_time is not None:
            if self.next_update_time > value:
                return
            
        self.next_update_time = value + timedelta(days=1)
        self.send_report(f"28 00 00 00 00 00 00 d7"
                         f"{value.year:04x} {value.month:02x} {value.day:02x}"
                         f"{value.hour:02x} {value.minute:02x} {value.second:02x}")
        self.poll()


def set_display(device, cpu, temp, date_time):
    if cpu is not None:
        device.set_cpu(cpu)
    if temp is not None:
        device.set_temp(temp)
    if date_time is not None:
        device.set_time(date_time)


def get_cpu_load():
    return int(psutil.cpu_percent(1))


def get_cpu_temp():
    count = 0
    temp = 0
    sensors = psutil.sensors_temperatures()
    for group in sensors.values():
        for sensor in group:
            if sensor.label == 'Tctl':
                count += 1
                temp += sensor.current
    return int(temp / count) if count > 0 else 0
    

def main(cpu, current_cpu, temp, current_temp, date_time, current_time, monitor):
    device = WirelessRT100()
    
    if monitor is not None:
        current_cpu = True
        current_temp = True
        current_time = True

    while True:
        if current_cpu:
            cpu = get_cpu_load()
        if current_temp:
            temp = get_cpu_temp()
        if current_time:
            date_time = 'NOW'

        set_display(device, cpu, temp, date_time)

        if monitor is None:
            break

        while True:
            time.sleep(monitor.update_period)
            if monitor.last_active + timedelta(minutes=2) >= datetime.now():
                break


if __name__ == "__main__":
    # support negative args
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit():
            sys.argv[i] = ' ' + arg

    parser = argparse.ArgumentParser()
    parser.add_argument('--cpu', type=int, help="Show custom cpu load, clipped to [0, 99]")
    parser.add_argument('--current-cpu', action="store_true", help="Show current CPU load")
    parser.add_argument('--temperature', type=int, help="Show custom temperature, will be clipped to [-99, 127]")
    parser.add_argument('--current-temperature', action="store_true", help="Show current CPU temperature")
    parser.add_argument('--time', type=str, help="Show date and time in iso format (1111-11-11T11:11)")
    parser.add_argument('--current-time', action="store_true", help="Show current time")
    parser.add_argument('--monitor', type=int, help="Update cpu and temperature every MONITOR seconds, time every 24 hours")
    args = parser.parse_args()

    monitor = None
    if args.monitor:
        monitor = KeyboardMonitor(args.monitor)

    while True:
        try:
            main(args.cpu, args.current_cpu, args.temperature, args.current_temperature, args.time, args.current_time, monitor)
        except Exception as e:
            print(e)

        if monitor is None:
            break

        time.sleep(10)
