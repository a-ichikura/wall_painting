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

        # 最初の一回でいいのでは？
        print(self.motion_service.getStiffnesses("Body"))
        for i in range(len(angles_list)):
            # setAnglesはnon-blocking, speedは速度の比率で、時間ではない.つまりsleep(speed)ではだめ
            #self.motion_service.setAngles(joint_name,angles_list[i],speed)
            print("{} {} {}".format(joint_name, ["{:5.2f}".format(x) for x in angles_list[i]], speed))
            # speed秒間動かすAPIはこっち？
            # http://doc.aldebaran.com/2-4/naoqi/motion/control-joint-api.html
            self.motion_service.angleInterpolation(joint_name,angles_list[i],speed,True)
            #time.sleep(speed+0.1)
            # OMAJINAI!!
            time.sleep(0.1)
            # 表示を綺麗に
            print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

        print("end up {}".format(motion_name))
        self.init_pose()
        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

    # 上のプログラムが角度をspeed秒かけて動かす，-> 動き終わるのをまって関数が返ってくる -> 次の関節角度を送る
    # ガクガク動く可能性がある．最初っから　len(angles_list) 個分の角度を送るという使い方をしたほうがきれいに動く可能性がある
    # ただし、全ての角度を送ってからでないと関数から帰ってこない。これでよいのか？
    def play_motion2(self,motion_name,json_name):
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

        print(self.motion_service.getStiffnesses("Body"))
        print("{} {}".format(joint_name, ["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))
        time_list = [0.4*(i+1) for i in range(len(angles_list))]
        print("{} -> time_list {}".format(joint_name, time_list))
        print([time_list]*len(angles_list))
        # 多分これでいい気がするけど，実機で確認が必要
        # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        self.motion_service.angleInterpolation(joint_name,list(map(list, zip(*angles_list))),[time_list]*len(angles_list),True)
        print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

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
        motion_name = input("please enter the motion name:")
        # /home/ichikura 以外でも使えるように
        json_name = os.path.dirname(os.path.realpath(__file__))+"/json/motion.json"
        #pepper.play_motion(motion_name,json_name)
        pepper.play_motion2(motion_name,json_name)
        command = input("please input start or end:") # command == は良くあるミス！
