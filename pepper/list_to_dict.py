import qi
import sys 
import time
import json
import collections as cl
import ndjson

json_name = "/home/ichikura/rosielab/pepper/json/motion.json"
with open(json_name) as f:
    data = ndjson.load(f)

print(type(data[0]))
print(data[0])


json_name = "/home/ichikura/rosielab/pepper/json/motion_2.json"
with open(json_name) as f:
    data = ndjson.load(f)

print(type(data[0][0]))
print(data[0][0])

json_name = "/home/ichikura/rosielab/pepper/json/motion_3.json"
with open(json_name) as f:
    data = ndjson.load(f)

print(type(data[0]))
print(data[0])


json_name = "/home/ichikura/rosielab/pepper/json/motion.json"
with open(json_name) as f:
    recorded_data = ndjson.load(f)

json_name = "/home/ichikura/rosielab/pepper/json/motion_4.json"
for i in range(len(recorded_data)):
    data = cl.OrderedDict(recorded_data[i])
    if i == 0:
        with open(json_name,"w") as f:
            writer=ndjson.writer(f)
            writer.writerow(data)
    else:
        with open(json_name,"a") as f:
            writer=ndjson.writer(f)
            writer.writerow(data)

with open(json_name) as f:
    data = ndjson.load(f)

print(type(data[0]))
print(data[0])

#json_name 
#with open(json_name,"w") as f:
#    writer = ndjson.writer(f)
#    writer.writerow(data[0])
