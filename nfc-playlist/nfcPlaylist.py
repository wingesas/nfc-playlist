#!/usr/bin/env python

import logging
import sys
import time
import nxppy
import json
import os
import mpd
import RPi.GPIO as GPIO
from logging.handlers import RotatingFileHandler

# defaults
LOG_FILENAME = "/var/log/nfcPlaylist.log"
MPD_HOST = "raspi2"
MPD_PORT = "6600"

# GPIO buttons
BUTTON_PREV = 18
BUTTON_PAUSE = 13
BUTTON_NEXT = 7

logger = logging.getLogger(__name__)

def button_pressed_event(channel):
    logger.info('button_pressed_event')
    if channel == BUTTON_PREV and GPIO.input(channel) == 1:
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        logger.info('button prev pressed')
        client.previous()
        client.close()
        client.disconnect()

    if channel == BUTTON_PAUSE and GPIO.input(channel) == 1:
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        logger.info('button pause pressed')
        client.pause()
        client.close()
        client.disconnect()

    if channel == BUTTON_NEXT and GPIO.input(channel) == 0:
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        logger.info('button next pressed')
        client.next()
        client.close()
        client.disconnect()

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_PREV, GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_PAUSE, GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_NEXT, GPIO.IN, GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_PREV, GPIO.RISING, callback=button_pressed_event, bouncetime=500)  # 500ms
    GPIO.add_event_detect(BUTTON_PAUSE, GPIO.FALLING, callback=button_pressed_event, bouncetime=500)  # 500ms
    GPIO.add_event_detect(BUTTON_NEXT, GPIO.FALLING, callback=button_pressed_event, bouncetime=500)  # 500ms

def setup_logging():
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=1048576, backupCount=3)  # 1024 * 1024 = 1MB
    formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Make a class we can use to capture stdout and sterr in the log
    class MyLogger(object):
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level

        def write(self, message):
            # Only log if there is a message (not just a new line)
            if message.rstrip() != "":
                self.logger.log(self.level, message.rstrip())

    sys.stdout = MyLogger(logger, logging.INFO)
    sys.stderr = MyLogger(logger, logging.ERROR)

def main():
    setup_logging()
    setup_gpio()

    try:
        while True:
            time.sleep(0.2)
    finally:
        GPIO.cleanup()

    # read json file which contains key/value pairs of card id and playlist name
    fileName = os.path.join(os.path.dirname(__file__), 'data.json')

    with open(fileName) as dataFile:
        data = json.load(dataFile)

    mifare = nxppy.Mifare()

    uidCurrent = None  # current uid of detected card
    logger.info('ready - waiting for mifare ...')

    while True:
        try:
            uid = mifare.select()

            if uid is not None and uidCurrent != uid:  # not same card as before?
                uidCurrent = uid
                logger.info("uid: " + str(uid))

                if uid in data.keys():
                    client = mpd.MPDClient()
                    client.connect(MPD_HOST, MPD_PORT)
                    client.clear()
                    client.load("beep")
                    client.play()
                    client.clear()

                    # call mpc with data[uid]
                    playlist = data[uid].get("playlist") if hasattr(data[uid], "get") else data[uid]
                    method = data[uid].get("method") if hasattr(data[uid], "get") else "load"
                    logger.info("playlist: " + str(playlist))

                    try:
                        if (method == "load"):
                            client.load(playlist)
                        else:
                            client.add(playlist)

                        client.play()
                    except mpd.CommandError, e:
                        logger.error("CommandError " + str(e))

                    # shutdown
                    client.close()
                    client.disconnect()
                else:
                    # insert new uid to file
                    data.update({uid: '__TODO__'})
                    with open(fileName, 'w') as outFile:
                        json.dump(data, outFile, indent=4)

        except nxppy.SelectError:
            pass

        time.sleep(0.2)

if __name__ == "__main__":
    main()
