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
# session.setClientAuthenticatorFactory(factory)
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

    def get_angles(self,name):
        angles = self.motion_service.getAngles(name,False)
        print(angles)
        return angles

    def record_angles(self,name="RArm",speed="0.4"):
        speed = float(speed)
        self.motion_service.setStiffnesses("Body",0.0)
        self.angles_list = []
        try:
            while True:
                angles = self.get_angles(name)
                self.angles_list.append(angles)
                time.sleep(speed)
        except KeyboardInterrupt:
            print("angles list is :{}".format(self.angles_list))
            return self.angles_list
            

    def save_json(self,motion_name,json_name,joint_name,speed):
        motion_list = [motion_name]
        ys = cl.OrderedDict()
        for i in range(len(motion_list)):
            data = cl.OrderedDict()
            data["angles"] = self.angles_list
            data["joint_name"] = joint_name
            data["speed"] = speed

            ys[motion_list[i]] = data

        with open(json_name,"a") as f:
            writer = ndjson.writer(f)
            writer.writerow(ys)

if __name__ == "__main__":
    print("started")
    pepper = Pepper()
    command = input("please enter your command:")
    if pepper.AL_get() != "disabled":
        pepper.AL_set("disabled")
        time.sleep(3.0)
    while not command == "end":
        joint_name = input("please enter the joint name.\n default = RArm:")
        speed = input("how much the speed is? \n default = 0.4:")
        pepper.record_angles(joint_name,speed)
        motion_name = input("please enter the motion name:")
        json_name = "/home/ichikura/rosielab/pepper/json/motion.json"
        pepper.save_json(motion_name,json_name,joint_name,speed)
        command == input("please input start or end:")
