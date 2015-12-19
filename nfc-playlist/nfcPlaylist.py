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

# Deafults
LOG_FILENAME = "/tmp/nfcPlaylist.log"
MPD_HOST = "localhost"
MPD_PORT = "6600"

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
mixer.init()

# read json file which contains key/value pairs of card id and playlist name
fileName = os.path.join(os.path.dirname(__file__), 'data.json')

with open(fileName) as dataFile:
    data = json.load(dataFile)

uidCurrent = None  # current uid of detected card
mifare = nxppy.Mifare()
logger.info('ready - waiting for mifare ...')

while True:
    try:
        uid = mifare.select()

        if uidCurrent != uid:  # not same card as before?
            uidCurrent = uid
            logger.info("uid: " + str(uid))

            if uid in data.keys():
                client = mpd.MPDClient()
                client.connect(MPD_HOST, MPD_PORT)
                client.clear()
                mixer.music.load(os.path.join(os.path.dirname(__file__), 'beep.mp3'))
                mixer.music.play()

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
        # no card detected; but uid current in use?
        if uidCurrent is not None:
            logger.info("playlist stop")
            mixer.music.load(os.path.join(os.path.dirname(__file__), 'beepDouble.mp3'))
            mixer.music.play()
            uidCurrent = None
            client = mpd.MPDClient()
            client.connect(MPD_HOST, MPD_PORT)
            client.stop()
            client.close()
            client.disconnect()

    time.sleep(1)
