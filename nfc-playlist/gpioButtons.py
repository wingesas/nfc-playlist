#!/usr/bin/env python

import logging
import sys
import time
import mpd
import RPi.GPIO as GPIO
from logging.handlers import RotatingFileHandler

# defaults
LOG_FILENAME = "/var/log/nfcPlaylist.log"
MPD_HOST = "raspi2"
MPD_PORT = "6600"

# GPIO buttons
BUTTON_PREV = 8
BUTTON_PAUSE = 13
BUTTON_NEXT = 7

doPause = True

logger = logging.getLogger(__name__)

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

def button_pressed_event(channel):

    if channel == BUTTON_PREV and GPIO.input(channel) == 0:
        logger.info('button prev pressed')

    if channel == BUTTON_NEXT and GPIO.input(channel) == 0:
        logger.info('button next pressed')

    if channel == BUTTON_PAUSE and GPIO.input(channel) == 0:
        logger.info('button pause pressed')

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_PREV, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_PAUSE, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_NEXT, GPIO.IN, GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_PREV, GPIO.RISING, callback=button_pressed_event, bouncetime=500)  # 500ms
    GPIO.add_event_detect(BUTTON_PAUSE, GPIO.FALLING, callback=button_pressed_event, bouncetime=500)  # 500ms
    GPIO.add_event_detect(BUTTON_NEXT, GPIO.FALLING, callback=button_pressed_event, bouncetime=500)  # 500ms

def main():
    setup_logging()
    setup_gpio()

    logger.info('ready - waiting for buttons ...')

    while True:
        time.sleep(0.2)

if __name__ == "__main__":
    main()
