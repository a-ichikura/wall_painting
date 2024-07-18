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

class Authenticator:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return a dictionary containing
    # login information with the keys 'user' and 'token'.
    def initialAuthData(self):
        return {'user': self.username, 'token': self.password}


class AuthenticatorFactory:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return an object with at least
    # the `initialAuthData` method.
    def newAuthenticator(self):
        return Authenticator(self.username, self.password)

class Pepper:

    def __init__(self):
        #self.app = qi.Application(sys.argv, url="tcp://133.11.216.52:9559")
        #
        # naoqi 2.5 have following erros
        #
        # AttributeError: 'Object' object has no attribute 'setClientAuthenticatorFactory'
        version = sys.argv[1]
        ip = sys.argv[2]
        if version == "2.9":
            url = "tcps://" + ip + ":9503"
            self.app = qi.Application(sys.argv, url=url)
            logins = ("nao", "nao")
            factory = AuthenticatorFactory(*logins)
            self.app.session.setClientAuthenticatorFactory(factory)
            self.app.start()
            self.autonomous_life = self.app.session.service("ALAutonomousLife")
            self.motion_service = self.app.session.service("ALMotion")
            self.posture_service = self.app.session.service("ALRobotPosture")
            self.audio_service = self.app.session.service("ALAudioPlayer")
            self.led_service = self.app.session.service("ALLeds")
            self.memory_service = self.app.session.service("ALMemory")
            self.blinking_service = self.app.session.service("ALAutonomousBlinking")
            self.tts_service = self.app.session.service("ALTextToSpeech")
            self.human_awareness = self.app.session.service("HumanAwareness")
            self.basic_awareness = self.app.session.service("BasicAwareness")
            
        elif version == "2.5":
            url = "tcp://" + ip + ":9559"
            self.session = qi.Session()
            self.session.connect(url)
            self.autonomous_life = self.session.service("ALAutonomousLife")
            self.motion_service = self.session.service("ALMotion")
            self.posture_service = self.session.service("ALRobotPosture")
            self.audio_service = self.session.service("ALAudioPlayer")
            self.led_service = self.session.service("ALLeds")
            self.memory_service = self.session.service("ALMemory")
            self.blinking_service = self.session.service("ALAutonomousBlinking")
            self.tts_service = self.app.session.service("ALTextToSpeech")

        self.tts_service.setVolume(0.5)
        self.tts_service.setParameter("pitchShift",1.4)
        self.tts_service.setParameter("speed",50)
        s = [self.app.session.service("ALAutonomousLife"), self.app.session.service("BasicAwareness")]
        for i in range(len(s)):
            print("line {}".format(i+1))
            x = s[i]
            print(x)
            print(dir(x))
            #print(x.getMethodList())
        
    def AL_get(self):
        life_status = self.autonomous_life.getState()
        print("Life state is:{}".format(life_status))
        return life_status

    def AL_set(self,state):
        self.autonomous_life.setState(state)
        print("Autonomous life has been {}".format(state))

    def get_volume(self):
        master_volume = self.audio_service.getMasterVolume()
        print(master_volume)

    def set_volume(self,value):
        self.audio_service.setMasterVolume(value)
        
    def init_pose(self):
        self.motion_service.setStiffnesses("Body",1.0)
        print("start to Stand Init")
        self.posture_service.goToPosture("Stand",2)
        self.blinking_service.setEnabled(True)
        time.sleep(2)
        print("end up Stand Init")

#これでframeの変化を求められそう
def print_human(pepper,humans):
    try:
        human = humans[0]
        print(dir(humans[0]))
        frame = human.headFrame.value()
        print(human.headFrame.value())
        pepper.motion_service._lookAt(frame)
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
    humansAround.connect(lambda humans: print_human(pepper,humans))

    while command != "end":
        time.sleep(1)
        pepper.init_pose()
        command = input("please enter your command:")
    #ctxFactory = pepper.app.session.service("ContextFactory")
    #focus = pepper.app.session.service("Focus")
    #ctx = ctxFactory.makeContext()
    #focusOwner = focus.take()
    #ctx.focus.setValue(focusOwner)
    #ctx.identity.setValue("my-app") # Unsure about this, let me know if it works for you
    # You can now use the ctx object for the API that you want
    #engageHuman = pepper.human_awareness.makeEngageHuman(ctx, human)
    #engageHuman.run()
    
