#!/usr/bin/python

#  Copyright (c) 2020 Hombrelab <me@hombrelab.com>

# watermeter-reader.py - read the GPIO pins for information about the water meter

import RPi.GPIO as GPIO
import os
import time
import logging
import paho.mqtt.publish as publish
import json

from datetime import datetime

CONSUMED = os.getenv('CONSUMED', 0)
BROKER_URL = os.getenv('BROKER_URL', 'host.name')
BROKER_PORT = os.getenv('BROKER_PORT', 1883)
TOPIC = os.getenv('TOPIC', 'home-assistant/watermeter-reader')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)

DATA_FILE = '/app/log/consumed.log'
LOG_FILE = '/app/log/info.log'

ELEMENT_LITERS_CONSUMED = 'litersConsumed'
ELEMENT_LITERS_TIMESTAMP = 'litersTimestamp'
ELEMENT_LAST_CONSUMED = 'lastConsumed'
ELEMENT_LAST_TIMESTAMP = 'lastTimestamp'
ELEMENT_PULSE = 'pulse'
ELEMENT_CONSUMED = 'consumed'
ELEMENT_TIMESTAMP = 'timestamp'

LITERS_DELTA = float(30)

data = {}

cycles = 0

liters_consumed = 0
liters_timestamp = float(datetime.now().timestamp())


def init():
    logging.info('Initialization started')

    init_data()

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        GPIO.add_event_detect(40, GPIO.RISING, callback=handler, bouncetime=350)

        logging.info('Event handling started')

        while True:
            time.sleep(0.05)
    except RuntimeError:
        logging.exception('Event handling error')

    GPIO.cleanup()


def handler(channel):
    global cycles

    time.sleep(0.05)

    if GPIO.input(40) != 1:
        logging.debug('Event handling ignored %s input', GPIO.input(40))

        return

    publish_data()


def init_data():
    global data
    global liters_consumed
    global liters_timestamp

    try:
        with open(DATA_FILE) as file:
            data = json.load(file)

            file.close()

        logging.info('Initialization read liters \'%s\' & consumed \'%s\'', data[ELEMENT_LITERS_CONSUMED], format_meter(int(data[ELEMENT_CONSUMED])))
    except Exception as exception:
        timestamp = datetime.now().timestamp()

        data = {
            ELEMENT_LITERS_CONSUMED: 0,
            ELEMENT_LITERS_TIMESTAMP: timestamp,
            ELEMENT_LAST_CONSUMED: int(CONSUMED),
            ELEMENT_LAST_TIMESTAMP: timestamp,
            ELEMENT_PULSE: 0,
            ELEMENT_CONSUMED: int(CONSUMED),
            ELEMENT_TIMESTAMP: timestamp
        }

        with open(DATA_FILE, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

            file.close()

        logging.info('Initialization stored liters \'%s\' & consumed \'%s\'', data[ELEMENT_LITERS_CONSUMED], format_meter(int(data[ELEMENT_CONSUMED])))

    if ELEMENT_LITERS_CONSUMED in data:
        liters_consumed = int(data[ELEMENT_LITERS_CONSUMED])

    if ELEMENT_LITERS_TIMESTAMP in data:
        liters_timestamp = float(data[ELEMENT_LITERS_TIMESTAMP])

    publish.single(topic=TOPIC, payload=json.dumps(data), qos=1, retain=False, hostname=BROKER_URL, port=int(BROKER_PORT))


def publish_data():
    global cycles
    global data
    global liters_consumed
    global liters_timestamp

    pulse = 1
    timestamp = datetime.now().timestamp()

    if abs(timestamp - liters_timestamp) >= LITERS_DELTA:
        liters_consumed = 0

    liters_consumed += pulse
    liters_timestamp = timestamp

    data[ELEMENT_LITERS_CONSUMED] = liters_consumed
    data[ELEMENT_LITERS_TIMESTAMP] = liters_timestamp
    data[ELEMENT_LAST_CONSUMED] = data[ELEMENT_CONSUMED]
    data[ELEMENT_LAST_TIMESTAMP] = data[ELEMENT_TIMESTAMP]
    data[ELEMENT_PULSE] = pulse
    data[ELEMENT_CONSUMED] = data[ELEMENT_CONSUMED] + pulse
    data[ELEMENT_TIMESTAMP] = timestamp

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

        file.close()

    publish.single(topic=TOPIC, payload=json.dumps(data), qos=1, retain=False, hostname=BROKER_URL, port=int(BROKER_PORT))

    logging.info('Event handler published and stored liters \'%s\' & consumed \'%s\'', data[ELEMENT_LITERS_CONSUMED], format_meter(int(data[ELEMENT_CONSUMED])))


def format_meter(value):
    total = str(value).zfill(8)

    cubic_meters = total[:5]
    cubic_millis = total[-3:]

    return '%s,%s' % (cubic_meters, cubic_millis)


logging.basicConfig(filename=LOG_FILE, level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    init()
