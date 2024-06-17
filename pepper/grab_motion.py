#! /usr/bin/env python


import qi
import sys 
import time

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
        self.app = qi.Application(sys.argv, url="tcps://10.0.0.4:9503")
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
        
    def init_pose(self):
        print("start to Stand Init")
        self.posture_service.goToPosture("Stand",1.0)
        time.sleep(3)
        
    def grab(self):
        print("Strat to grasp")
        handName = "RHand"
        stiffnesses = 1.0
        self.motion_service.setStiffnesses(handName,stiffnesses)
        self.motion_service.closeHand(handName)
        self.get_angles("RHand")

    def close_hand(self,handName,angles,speed):
        self.motion_service.setStiffnesses(handName,0)
        self.motion_service.setAngles(handName,angles,speed)
        

if __name__ == "__main__":
    print("started")
    pepper = Pepper()
    command = input("please enter your command:")
    if pepper.AL_get() != "disabled":
        pepper.AL_set("disabled")
        time.sleep(3.0)
        pepper.init_pose()
    if command == "grab":
        try:
            while True:
                #pepper.grab()
                pepper.close_hand("RHand",0.5,1.0)
        except KeyboardInterrupt:
            sys.exit
