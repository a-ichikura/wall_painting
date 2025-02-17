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

        self.tts_service.setVolume(0.8)
        self.tts_service.setParameter("pitchShift",1.4)
        self.tts_service.setParameter("speed",50)
        
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


        time_list = [0.4*(i+1) for i in range(len(angles_list))]

        ##time_listにangles_listをかける
        # 多分これでいい気がするけど，実機で確認が必要
        # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        self.motion_service.angleInterpolation(joint_name,list(map(list, zip(*angles_list))),[time_list]*len(angles_list),True)
        #print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

        print("end up {}".format(motion_name))

        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

    def draw_motion(self,json_name):
        self.look([0,0])
        print("start to move its arm to paint")
        motion_list = ["draw","draw_2","draw_3"]
        motion_name = random.choice(motion_list)
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
        head_time_list = [0.7,0.7]
        if shoulder_p_change >= 0:
            #左
            if shoulder_r_change >0:
                print("left down")
                head_angle_list = [0,0.25]
                self.motion_service.angleInterpolation("Head",head_angle_list,head_time_list,True)
            #右
            else:
                print("right down")
                head_angle_list = [-0.4,0.25]
        #上方向
        else:
            if shoulder_r_change >0:
                print("left up")
                head_angle_list = [0,-0.15]
            else:
                print("right up")
                head_angle_list = [-0.4,-0.15]
        self.motion_service.angleInterpolation("Head",head_angle_list,head_time_list,True)
        #print(self.motion_service.getStiffnesses("Body"))

        #print("{} {}".format(joint_name, ["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))
        
        time_list = [0.4*(i+1) for i in range(len(angles_list))]
        #print("{} -> time_list {}".format(joint_name, time_list))

        #print([time_list]*len(angles_list))
        # 多分これでいい気がするけど，実機で確認が必要
        # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        #1秒ずつくらいにわけてリストを送る 3分割すればよいのでは？
        print("time:\n{}".format(time_list))
        print("angles:\n{}".format(angles_list))
        num = 10
        devided_time_list = time_list[:num]
        for i in range((len(time_list)//num)+1):
            print(i)
            if i != len(time_list)//num:
                devided_angles_list = angles_list[i*num:(i+1)*num]
                #print("d_time:\n{}".format(devided_time_list))
                #print("d_angles:\n{}".format(devided_angles_list))
                #print("d_zip:\n{}".format(list(map(list,zip(*devided_angles_list)))))
            elif i == len(time_list)//num:
                devided_time_list = devided_time_list[:(len(time_list)%num)]
                devided_angles_list = angles_list[i*num:]
            try:
                self.motion_service.angleInterpolation(joint_name,list(zip(*devided_angles_list)),[devided_time_list]*(len(devided_angles_list[0])),True)
            except:
                pass
            self.look_change()
            self.sing_sound()
        #self.motion_service.angleInterpolation(joint_name,list(map(list, zip(*angles_list))),[time_list]*len(angles_list),True)
        
        #print("     {}".format(["{:5.2f}".format(x) for x in self.motion_service.getAngles(joint_name, False)]))

        print("end up {}".format(motion_name))
        self.init_pose()
        time.sleep(0.3)
        self.motion_service.setStiffnesses("Body",0.0)

    def look(self,head_angle_list):
        print("start to look at the interactor child")
        self.motion_service.setStiffnesses("Body",1.0)

        head_time_list = [0.7,0.7]
        self.motion_service.angleInterpolation("Head",head_angle_list,head_time_list,True)

    def look_change(self):
        print("start to change the head position")
        speed = 0.05
        changes = [round(random.uniform(0.15,-0.2),2),round(random.uniform(0.1,-0.1),2)]
        self.motion_service.changeAngles("Head",changes,speed)
        
    def play_sound(self,filename):
        fileId = self.audio_service.loadFile(filename)
        self.audio_service.play(fileId)

    def help_sound(self):
        filename = "/home/nao/aiko/pepper_so_sad.mp3"
        self.play_sound(filename)

    def happy_sound(self):
        filename = "/home/nao/aiko/pepper_happy.mp3"
        self.play_sound(filename)

    def sing_sound(self):
        num = ["","2","3"]
        filename = "/home/nao/aiko/pepper_whistling" + random.choice(num) + ".mp3"
        self.play_sound(filename)

    def curious_sound(self):
        filename = "/home/nao/aiko/pepper_curious.mp3"
        self.play_sound(filename)

    def change_led(self,group,r,g,b,duraion):
        self.led_service.fadeRGB(group,r,g,b,duraion)

    def help_led(self):
        self.blinking_service.setEnabled(False)
        group = "FaceLeds"
        ##red, blue, yellow
        color_list = ["pink","blue","yellow"]
        self.color = random.choice(color_list)
        if self.color == "pink":
            color_rgb = [255,51,255]
        elif self.color == "blue":
            color_rgb = [0,0,255]
        elif self.color == "yellow":
            color_rgb = [255,215,0]
        duration = 0.5
        self.change_led(group,color_rgb[0],color_rgb[1],color_rgb[2],duration)

    def say_color(self):
        self.tts_service.say(self.color + "!")
        time.sleep(1)

    def say_okay(self):
        self.tts_service.say("OK!")
        
    def waiting_hand_touch(self):
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onhandTouched,"TouchChanged"))
        self.detected_hand = False
        for i in range(0,20):
            if self.detected_hand == True:
                self.look([-0.9,0.25])
                print("exit waiting hand touch in 20 seconds")
                time.sleep(10)
                break
            else:
                self.say_color()
                time.sleep(1)
                continue
        print("exited waiting hand touch")
        self.change_led("FaceLeds",255,255,255,0.5)
        self.blinking_service.setEnabled(True)

    def waiting_hand_touch_low(self):
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onhandTouched,"TouchChanged"))
        self.detected_hand = False
        for i in range(0,20):
            if self.detected_hand == True:
                self.look([-0.9,0.25])
                print("exit waiting hand touch in 50 seconds")
                time.sleep(10)
                self.look([0,0])
                for l in range(0,4):
                    time.sleep(10)
                    self.look_change()
                    self.sing_sound()
                break
            else:
                self.say_color()
                time.sleep(1)
                continue
        print("exited waiting hand touch")
        self.change_led("FaceLeds",255,255,255,0.5)
        self.blinking_service.setEnabled(True)
    
    def waiting_head_touch(self):
        print("start waiting head touch")
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onheadTouched,"TouchChanged"))
        self.detected_head = False
        self.curious_sound()
        for i in range(0,20):
            if self.detected_head == True:
                print("exit waiting head touch soon")
                time.sleep(5)
                break
            else:
                time.sleep(1)
                self.curious_sound()
                continue
        print("exited waiting head touch")
        

    def onheadTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.

        """
        # Disconnect to the event when talking,
        # to avoid repetitions
        self.touch.signal.disconnect(self.id)

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])

        self.detect_head(touched_bodies)
        
    def onhandTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.

        """
        # Disconnect to the event when talking,
        # to avoid repetitions
        self.touch.signal.disconnect(self.id)

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])

        self.detect_hand(touched_bodies)

    def detect_hand(self,touched_bodies):
        if (touched_bodies ==[]):
            self.id = self.touch.signal.connect(functools.partial(self.onhandTouched, "TouchChanged"))
            return 
        body = touched_bodies[0]
        if body == "RArm":
            print("the right arm is touched")
            self.detected_hand = True
            self.motion_service.setStiffnesses("RArm",0.0)
            self.change_led("FaceLeds",255,255,255,0.5)
            return
        else:
            self.id = self.touch.signal.connect(functools.partial(self.onhandTouched, "TouchChanged"))
            return

    def detect_head(self,touched_bodies):
        if (touched_bodies ==[]):
            self.id = self.touch.signal.connect(functools.partial(self.onheadTouched, "TouchChanged"))
            return
        body = touched_bodies[0]
        if body == "Head":
            print("The head is touched")
            self.motion_service.setStiffnesses("RArm",1.0)
            i = 0
            for i in range(0,2):
                self.led_service.rotateEyes(0x00FFFFFF,1.0,0.5)
                self.say_okay()
                i=i+1
            self.change_led("FaceLeds",255,255,255,0.5)
            self.detected_head = True
        else:
            self.id = self.touch.signal.connect(functools.partial(self.onheadTouched, "TouchChanged"))
            return


# for python2 support
# https://stackoverflow.com/questions/21731043/use-of-input-raw-input-in-python-2-and-3
try:
    input = raw_input
except NameError:
    pass
