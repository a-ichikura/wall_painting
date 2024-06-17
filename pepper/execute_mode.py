#! /usr/bin/env python


import qi
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
        self.app = qi.Application(sys.argv, url="tcps://10.0.0.6:9503")
        logins = ("nao", "nao")
        factory = AuthenticatorFactory(*logins)
        self.app.session.setClientAuthenticatorFactory(factory)
        self.app.start()
        self.autonomous_life = self.app.session.service("ALAutonomousLife")
        self.motion_service = self.app.session.service("ALMotion")
        self.posture_service = self.app.session.service("ALRobotPosture")

    def AL_get(self):
        life_status = self.autonomous_life.getState()
        print("Life state is:{}".format(life_status))
        return life_status

    def AL_set(self,state):
        self.autonomous_life.setState(state)
        print("Autonomous life has been {}".format(state))

    def init_pose(self):
        print("start to Stand Init")
        self.posture_service.goToPosture("Stand",1.0)
        time.sleep(3)
    
    def play_motion(self,motion_name,json_name):        
        with open(json_name) as f:
            data = ndjson.load(f)

        for i in range(len(data)):
            recorded_motion = list(data[i].keys())[0]
            if recorded_motion == motion_name:
                angles_list = data[i][recorded_motion]["angles"]
                joint_name = data[i][recorded_motion]["joint_name"]
                speed = float(data[i][recorded_motion]["speed"])
        print(angles_list)

        self.motion_service.setStiffnesses("Body",1.0)
        
        print("start to {}".format(motion_name))
        
        for i in range(len(angles_list)):
            print(self.motion_service.getStiffnesses("Body"))
            self.motion_service.setAngles(joint_name,angles_list[i],speed)
            print(angles_list[i])
            time.sleep(speed)

        print("end up {}".format(motion_name))
        self.init_pose()
        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

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
        motion_name = input("please enter the motion name:")
        json_name = "/home/ichikura/rosielab/pepper/json/motion.json"
        pepper.play_motion(motion_name,json_name)
        command == input("please input start or end:")
