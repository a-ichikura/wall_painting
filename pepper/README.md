How to use

# 1. Setting

Prease rewrite the IP address of Pepper in `practice_mode.py` and `execute_mode.py`.
```
self.app = qi.Application(sys.argv, url="tcps://XX.XX.XX.XX:9503")
```

# 2. How to record a motion
For pepper 2.9, try to use python3.
Enter "start", "joint_name", and "speed."
Default setting of the joint name is "RArm", and one of the speed is 0.4.

```
python3 practice_mode.py

please enter your command: "start" [ENTER]

please enter the joint name.
default = RArm: "LArm" [ENTER]

how much the speed is?
default = 0.4: "0.4" [ENTER]
```

You can choose any joint names as follows.
http://doc.aldebaran.com/2-0/family/juliette_technical/joints_juliette.html

If the motion is correct, decide the name of motion.
```
please enter the motion name: "example1"
```

Then the named motion will be saved in a json file.
If you want to change the name of a json file, you can change in the main function.


# 3. How to play a motion
You can play the recorded motion as follows.
```
python3 execute_mode.py

please enter your command: "start" [ENTER]

please eneter the motion name: [the name of recorded motion name]
```

> [!CAUTION]
> The interactive mode will be `disabled` before practice or execute. \n
> `qi` should be install in advance. If you do not have `qi`, try
> ```
> pip install qi
> ```
