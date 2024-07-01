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
        time.sleep(7)
        print("end up Stand Init")

    def soak_motion(self,json_name):
        print("start to move its arm into the basket.")
        motion_name = "soak_look"
        with open(json_name) as f:
            data = ndjson.load(f)

        for i in range(len(data)):
            recorded_motion = list(data[i].keys())[0]
            if recorded_motion == motion_name:
                angles_list = data[i][recorded_motion]["angles"]
                joint_name = data[i][recorded_motion]["joint_name"]
                speed = float(data[i][recorded_motion]["speed"])
        #print(angles_list)

        self.motion_service.setStiffnesses("Body",1.0)

        print("start to {}".format(motion_name))

        print(self.motion_service.getStiffnesses("Body"))
        ##今のjoint_nameのアングルを得る
        print("{} {}".format(joint_name, ["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))
        ## time_listを表示する ＝　何個アングルが入っているかを見る
        time_list = [0.4*(i+1) for i in range(len(angles_list))]
        print("{} -> time_list {}".format(joint_name, time_list))

        ##time_listにangles_listをかける
        print([time_list]*len(angles_list))
        # 多分これでいい気がするけど，実機で確認が必要
        # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        self.motion_service.angleInterpolation(joint_name,list(map(list, zip(*angles_list))),[time_list]*len(angles_list),True)
        #print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

        print("end up {}".format(motion_name))
        self.init_pose()
        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

    def draw_motion(self,json_name):
        print("start to move its arm to paint")
        motion_name = "draw"
        with open(json_name) as f:
            data = ndjson.load(f)

        for i in range(len(data)):
            recorded_motion = list(data[i].keys())[0]
            if recorded_motion == motion_name:
                angles_list = data[i][recorded_motion]["angles"]
                joint_name = data[i][recorded_motion]["joint_name"]
                speed = float(data[i][recorded_motion]["speed"])
        #print(angles_list)

        ##動きをrandomにする
        
        seed = [1,-1]
        shoulder_p_change = random.uniform(0,0.3)*random.choice(seed)
        shoulder_r_change = random.uniform(0.3,0.4)*random.choice(seed)
        change_list = [shoulder_p_change,shoulder_r_change]
        add_list = change_list + [0,0,0,0]
        
        print("shoulder p change:{}\n shoulder_r_change:{}".format(shoulder_p_change,shoulder_r_change))
        angle_list_ = [x + add_list for x in angles_list]
        
        angles_list = [[num1 + num2 for num1,num2 in zip(angles_list[i],add_list)] for i in range(len(angles_list)) if i >= 10 and i <= 50]
        
        self.motion_service.setStiffnesses("Body",1.0)

        print("start to {}".format(motion_name))

        ##頭の方向を変えてみる
        ##下方向
        if shoulder_p_change >= 0:
            #左
            if shoulder_r_change >0:
                print("left down")
                self.motion_service.setAngles("Head",[0.8,0.15],0.4)
            #右
            else:
                print("right down")
                self.motion_service.setAngles("Head",[0.8,-0.15],0.4)
        #上方向
        else:
            if shoulder_r_change >0:
                print("left up")
                self.motion_service.setAngles("Head",[-0.8,0.15],0.4)
            else:
                print("right up")
                self.motion_service.setAngles("Head",[-0.8,-0.15],0.4)
                
        #print(self.motion_service.getStiffnesses("Body"))
        ##今のjoint_nameのアングルを得る
        #print("{} {}".format(joint_name, ["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))
        ## time_listを表示する ＝　何個アングルが入っているかを見る
        time_list = [0.4*(i+1) for i in range(len(angles_list))]
        #print("{} -> time_list {}".format(joint_name, time_list))

        ##time_listにangles_listをかける
        #print([time_list]*len(angles_list))
        # 多分これでいい気がするけど，実機で確認が必要
        # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        self.motion_service.angleInterpolation(joint_name,list(map(list, zip(*angles_list))),[time_list]*len(angles_list),True)
        #print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

        print("end up {}".format(motion_name))
        self.init_pose()
        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

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
        json_name = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')+"/json/motion.json"
        #pepper.soak_motion(json_name)
        pepper.draw_motion(json_name)
        command = input("please input start or end:") # command == は良くあるミス！
