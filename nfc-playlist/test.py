#!/usr/bin/env python2.7

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# 18
while True:
    input_state = GPIO.input(7)
    if input_state == 0:
        print('4 pressed')

    input_state = GPIO.input(13)
    if input_state == False:
        print('13 pressed')

    time.sleep(0.2)
