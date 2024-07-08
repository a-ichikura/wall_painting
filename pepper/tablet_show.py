#! /usr/bin/env python
# -*- coding: utf-8 -*-


import qi
import os
import sys 
import time
import json
import collections as cl
import ndjson

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

# Connect to the robot fails at app.start() => RuntimeError: disconnected


# This doesn't work either => RuntimeError: disconnected
# session = qi.Session()
# logins = ("nao", "OMITTED")
# factory = AuthenticatorFactory(*logins)
#1;5202;0c# session.setClientAuthenticatorFactory(factory)
# session.connect("tcp://192.168.1.59:9503")

class Pepper:

    def __init__(self):
        #self.app = qi.Application(sys.argv, url="tcp://133.11.216.52:9559")
        #
        # naoqi 2.5 have following erros
        #
        # AttributeError: 'Object' object has no attribute 'setClientAuthenticatorFactory'
        self.app = qi.Application(sys.argv, url="tcps://10.0.0.4:9503")
        logins = ("nao", "nao")
        factory = AuthenticatorFactory(*logins)
        self.app.session.setClientAuthenticatorFactory(factory)
        #
        self.app.start()
        self.autonomous_life = self.app.session.service("ALAutonomousLife")
        self.motion_service = self.app.session.service("ALMotion")
        self.posture_service = self.app.session.service("ALRobotPosture")
        self.tablet_service = self.app.session.service("ALTabletService")
        
    def AL_get(self):
        life_status = self.autonomous_life.getState()
        print("Life state is:{}".format(life_status))
        return life_status

    def AL_set(self,state):
        self.autonomous_life.setState(state)
        print("Autonomous life has been {}".format(state))

    def init_pose(self):
        self.motion_service.setStiffnesses("Body",1.0)
        print("start to Stand Init")
        self.posture_service.goToPosture("Stand",1.0)
        time.sleep(3)
        print("end up Stand Init")
    
    def tablet_show(self):
        try:
        # Display a local web page located in boot-config/html folder
        # The ip of the robot from the tablet is 198.18.0.1
            self.tablet_service.showWebview("http://10.0.0.5/apps/myapp/preloading_dialog.html")

            time.sleep(3)
            
            script = """
            var name = prompt("Please enter your name", "Harry Pepper");
            ALTabletBinding.raiseEvent(name)
            """

            # Don't forget to disconnect the signal at the end
            signalID = 0
            
            # function called when the signal onJSEvent is triggered
            # by the javascript function ALTabletBinding.raiseEvent(name)
            def callback(event):
                print ("your name is:".format(event))
                promise.setValue(True)

            promise = qi.Promise()

            # attach the callback function to onJSEvent signal
            signalID = self.tablet_service.onJSEvent.connect(callback)

            # inject and execute the javascript in the current web page displayed
            self.tablet_service.executeJS(script)

            try:
                promise.future().hasValue(30000)
            except RuntimeError:
                raise RuntimeError('Timeout: no signal triggered')

        except Exception as e:
            print ("Error was:".format(e))

        # Hide the web view
        self.tablet_service.hideWebview()
        # disconnect the signal
        self.tablet_service.onJSEvent.disconnect(signalID)



        
# for python2 support
# https://stackoverflow.com/questions/21731043/use-of-input-raw-input-in-python-2-and-3
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
    while not command == "end":
        pepper.tablet_show()
        command = input("please enter your command:")
