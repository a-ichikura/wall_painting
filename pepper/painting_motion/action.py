#! /usr/bin/env python
# -*- coding: utf-8 -*-


import qi
import os
import sys 
import time
import json
import collections as cl
import ndjson
import random
import functools
import asyncio
import logging
from core import Pepper

try:
    input = raw_input
except NameError:
    pass

if __name__ == "__main__":
    print("started")
    pepper = Pepper()
    command = input("please enter your command:")
    if pepper.AL_get() != "disabled":
        pepper.AL_set("disabled")
        time.sleep(3.0)
    #pepper.AL_set("solitary")
    pepper.init_pose()
    pepper.change_led("EarLeds",255,255,0,0.5)
    time.sleep(1)
    count = 1
    while not command == "end":
        ear_led = random.randint(0,1)
        if ear_led == 0 or count == 3: #描くモードon
            print("helping mode ON")
            pepper.change_led("EarLeds",0,0,255,0.5)
            pepper.help_sound()
            pepper.help_led()
            pepper.waiting_hand_touch()
            pepper.waiting_head_touch()
            if pepper.detected_head ==True:
                pepper.motion_service.setStiffnesses("Body",1.0)
                print("start to Stand Init")
                pepper.posture_service.goToPosture("Stand",1.0)
                pepper.blinking_service.setEnabled(True)
                time.sleep(2)
                print("end up Stand Init")
                pepper.happy_sound()
            pepper.change_led("EarLeds",0,255,0,0.5)
            time.sleep(10)
            count = 1
        elif ear_led == 1 and count < 3:
            wait_time = random.randint(15,20)
            print("I will wait in {} seconds".format(wait_time))
            count = count +1
            time.sleep(wait_time)    
