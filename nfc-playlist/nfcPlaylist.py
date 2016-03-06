#!/usr/bin/env python

import logging
import logging.handlers
import sys
import time
import nxppy
import json
import os
import mpd
from pygame import mixer
import RPi.GPIO as GPIO

# Deafults
LOG_FILENAME = "/tmp/nfcPlaylist.log"
MPD_HOST = "raspi2"
MPD_PORT = "6600"
BUTTON_PREV = 7
BUTTON_NEXT = 8
BUTTON_PAUSE = 13

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
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

logger.info('starting ...')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON_PREV, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_NEXT, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_PAUSE, GPIO.IN, GPIO.PUD_UP)

isButtonPrevPressed = False
isButtonNextPressed = False
isButtonPausePressed = False

mixer.init()

# read json file which contains key/value pairs of card id and playlist name
fileName = os.path.join(os.path.dirname(__file__), 'data.json')

with open(fileName) as dataFile:
    data = json.load(dataFile)

mifare = nxppy.Mifare()
logger.info('ready - waiting for mifare ...')

while True:
    try:
        uid = mifare.select()
        logger.info("uid: " + str(uid))

        if uid is not None:  # not same card as before?
            logger.info("uid: " + str(uid))

            if uid in data.keys():
                # mixer.music.load(os.path.join(os.path.dirname(__file__), 'beep.mp3'))
                # mixer.music.play()

                client = mpd.MPDClient()
                client.connect(MPD_HOST, MPD_PORT)
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

    # isButtonPrevPressed = False if GPIO.input(BUTTON_PREV) == 1 else True

    if GPIO.input(BUTTON_PREV) == 0:
        isButtonPrevPressed = True
        logger.info('button prev pressed')
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        client.previous()
        client.close()
        client.disconnect()

    if GPIO.input(BUTTON_NEXT) == 0:
        isButtonPrevPressed = True
        logger.info('button next pressed')
        client = mpd.MPDClient()
        client.connect(MPD_HOST, MPD_PORT)
        client.next()
        client.close()
        client.disconnect()

    if GPIO.input(BUTTON_PAUSE) == 0:
        isButtonPrevPressed = True
        logger.info('button pause pressed')
        # client.pause(0)
        # mixer.music.load(os.path.join(os.path.dirname(__file__), 'beepDouble.mp3'))
        # mixer.music.play()
        # client.pause()
        # MPDClient.pause(pause)
        # Toggles pause/resumes playing, PAUSE is 0 or 1.

        # MPDClient.stop()
        # Stops playing.

    time.sleep(1)
