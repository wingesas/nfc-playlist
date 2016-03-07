#!/usr/bin/env python2.7

import RPi.GPIO as GPIO
import time

BUTTON_PREV = 7
BUTTON_NEXT = 18
BUTTON_PAUSE = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON_PREV, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_NEXT, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_PAUSE, GPIO.IN, GPIO.PUD_UP)

while True:
    if GPIO.input(BUTTON_PREV) == 0:
        print('BUTTON_PREV')

    if GPIO.input(BUTTON_NEXT) == 0:
        print('BUTTON_NEXT')

    if GPIO.input(BUTTON_PAUSE) == 0:
        print('BUTTON_PAUSE')

    time.sleep(0.2)
