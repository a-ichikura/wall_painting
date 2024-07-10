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

#これでframeの変化を求められそう
def print_human(humans):
    try:
        human = humans[0]
        frame = human.headFrame.value()
        print(frame)
    except IndexError as e:
        print("no human")
    
if __name__ == "__main__":
    print("started")
    pepper = Pepper()
    command = input("please enter your command:")
    if pepper.AL_get() != "disabled":
        pepper.AL_set("disabled")
        time.sleep(3.0)
    #pepper.AL_set("solitary")
    humansAround = pepper.human_awareness.humansAround
    humans = humansAround.value()
    humansAround.connect(lambda humans: print_human(humans))
    
    pepper.init_pose()
    ##start tracking

    pepper.motion_service.setExternalCollisionProtectionEnabled("RArm",False)
    pepper.change_led("EarLeds",255,255,0,0.5)
    time.sleep(1)
    count = 1
    while not command == "end":
        ear_led = random.randint(0,1)
        if ear_led == 0 or count == 1: #描くモードon
            print("helping mode ON")
            pepper.change_led("EarLeds",0,0,255,0.5)
            json_name = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')+"/json/motion.json"
            pepper.curious_sound()
            #pepper.soak_motion(json_name)
            #pepper.draw_motion(json_name)
            pepper.happy_sound()
            pepper.change_led("EarLeds",0,255,0,0.5)
            time.sleep(10)

            
            time.sleep(0.5)
            count = 1
            
        elif ear_led == 1 and count < 3:
            wait_time = random.randint(15,20)
            print("I will wait in {} seconds".format(wait_time))
            count = count +1
            time.sleep(wait_time)
        
            time.sleep(0.5)
