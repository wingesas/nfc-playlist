#!/usr/bin/env python

import logging
import logging.handlers
import argparse
import sys
import time
import nxppy
import json
import os
import mpd

# Deafults
LOG_FILENAME = "/tmp/nfcPolling.log"
LOG_LEVEL = logging.INFO  # "DEBUG" or "WARNING"
MPD_HOST = "localhost"
MPD_PORT = "6600"

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="NXP NFC Polling - Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

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

# read json file which contains key/value pairs of card id and playlist name
fileName = os.path.join(os.path.dirname(__file__), 'data.json')

with open(fileName) as dataFile:
    data = json.load(dataFile)

uidCurrent = None  # current uid of detected card
mifare = nxppy.Mifare()

while True:
    try:
        uid = mifare.select()

        if uidCurrent != uid:  # not same card as before?
            uidCurrent = uid
            if uid in data.keys():
                client = mpd.MPDClient()
                client.connect(MPD_HOST, MPD_PORT)
                client.clear()

                # call mpc with data[uid]
                playlist = data[uid].get("playlist") if data[uid].get("playlist") else data[uid]
                method = data[uid].get("method")

                try:
                    if (method or method == "load"):
                        client.load(data[uid])
                    else:
                        client.add(data[uid])

                    client.play()
                except mpd.CommandError, e:
                    logger.info("CommandError " + str(e))

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
            uidCurrent = None
            client = mpd.MPDClient()
            client.connect(MPD_HOST, MPD_PORT)
            client.stop()
            client.close()
            client.disconnect()

    time.sleep(1)
