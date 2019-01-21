#!/usr/bin/env python
"""
Read Paxcounter debug data from serial port and write it to a file
after some calculations.

TODO: cleanup and reorganise
TODO: add argparse and --quiet / --verbose etc switches.
"""
import serial
import datetime
import time
import pytz
import json
import re
import argparse
import requests
import logging as log

baudrate = 115200  # TODO: to args
MAX_AGE = 10  # TODO: to args

P = re.compile(' (new|known) +(WiFi|BLTH) +RSSI +(-[\d]+)dBi.*MAC ([\d\w]{8,12}) ')
headers = {'User-Agent': 'paxcounter/0.0.1'}

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=str, required=True, help="serial port, e.g. /dev/tty.SLAB_USBtoUART")
parser.add_argument("--url", type=str, help="URL where data is POSTed")
parser.add_argument("--jsonlog", type=str, help="file where psrsed data in JSON is saved")
parser.add_argument("--seriallog", type=str, help="file where all data from serial is saved")
parser.add_argument("--interval", type=int, default=10, help="time after the data isis POSTed")
parser.add_argument('-v', '--verbosity', default=0, action="count",
                    help="increase output verbosity (e.g., -vv is more than -v)")
args = parser.parse_args()

loglevel = 50 - args.verbosity * 10
if args.verbosity:
    log.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=loglevel)
else:
    log.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")
log.info(f'Log level: {loglevel}')


def parse_line(line):
    """
    [I][macsniff.cpp:124] mac_add(): known WiFi RSSI -73dBi -> MAC 98B3E5FB -> Hash 36A0 -> WiFi:10  BLTH:13 -> 50980 Bytes left
    [I][macsniff.cpp:124] mac_add(): known BLTH RSSI -81dBi -> MAC 36FC8190 -> Hash 6720 -> WiFi:10  BLTH:13 -> 51160 Bytes left
    [I][macsniff.cpp:130] mac_add(): known BLTH RSSI -81dBi -> MAC D86ABF895CF4 -> Hash 8C27 -> WiFi:8  BLTH:9 -> 51356 Bytes left
    [I][macsniff.cpp:130] mac_add(): new   WiFi RSSI -78dBi -> MAC 93F5B4DAF1B4 -> Hash DBEB -> WiFi:9  BLTH:9 -> 51344 Bytes left
    """
    m = P.search(line)
    if m:
        rmac = m.group(4)
        n = 2
        # Reverse hex bytes since they come fron Paxcounter LSB first
        mac = ''.join([rmac[i:i + n] for i in range(len(rmac) - 2, -1, -n)])
        data = {
            'new': True if m.group(1) == 'new' else False,
            'type': m.group(2),
            'rssi': int(m.group(3)),
            'mac': mac,
        }
        return data
    else:
        return None


def get_serial(port, baudrate=115200):
    stop_trying_time = time.time() + 10
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate  # TODO: to args

    while stop_trying_time > time.time() and ser.is_open is False:
        try:
            ser.open()
            ser.flushInput()
        except serial.serialutil.SerialException as err:
            pass
        time.sleep(0.2)
    if ser.is_open:
        return ser
    else:
        log.critical(f'Could not open port {port}')
        exit(1)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_now():
    return pytz.UTC.localize(datetime.datetime.utcnow())


def get_age(ts):
    age = (get_now() - ts).total_seconds()
    return age


ser = get_serial(args.port)
devs = {}
lines = []
last_cleanup = time.time()
running = True

while running:
    line = ''
    try:
        line = ser.readline().decode("utf-8").strip()
    except UnicodeDecodeError as err:
        log.info(err)
        continue
    except serial.serialutil.SerialException as err:
        log.critical(err)
        log.critical('Exiting now')
        last_cleanup = 0
        running = False
    line = line.strip()
    lines.append(line)
    log.debug(line)
    ts = get_now()
    if line.find('mac_add') > 0:
        data = parse_line(line)
        if data['type'].lower() in ['wifi', 'blth']:
            data['time'] = ts
            rssi = data.pop('rssi')
            mac = data['mac']
            if mac not in devs:
                devs[mac] = data
                devs[mac].pop('new')
                devs[mac]['rssi_min'] = devs[mac]['rssi_max'] = rssi
                devs[mac]['count'] = 1
            else:
                devs[mac]['count'] += 1
                if devs[mac]['rssi_min'] > rssi:
                    devs[mac]['rssi_min'] = rssi
                if devs[mac]['rssi_max'] < rssi:
                    devs[mac]['rssi_max'] = rssi
    if time.time() - last_cleanup > args.interval:
        json_data = json.dumps(devs, default=json_serial)
        log.info(json_data)
        # TODO: This this should happen in a thread:
        if args.url:
            try:
                res = requests.post(args.url, data=json_data, headers={'Content-Type': 'application/json'})
                log.info(f'{res.status_code} {res.text}')
                # requests.post(args.url, json=devs, headers=headers)
            except requests.exceptions.ConnectionError as err:
                log.error(f'Request failed {err}')
        if args.jsonlog is not None:
            if args.jsonlog == '':
                fname = datetime.datetime.utcnow().strftime('paxjson-%Y%m%d.txt')
            else:
                fname = args.jsonlog
            with open(fname, 'at') as f:
                f.write(json_data + '\n')
        if args.seriallog is not None:
            if args.seriallog == '':
                fname = datetime.datetime.utcnow().strftime('paxserial-%Y%m%d.txt')
            else:
                fname = args.seriallog
            with open(fname, 'at') as f:
                f.write('\n'.join(lines) + '\n')
        last_cleanup = time.time()
        devs = {}
