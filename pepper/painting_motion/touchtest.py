import sys
import qi
app = qi.Application(sys.argv, url="tcp://10.0.0.3:9559")
app.start()
memory_service = app.session.service("ALMemory")

# Listen to public addresses on a random port,                                                 
# so that services registered from here are accessible.                                        
app.session.listen("tcp://0.0.0.0:0")

# An object that will be registered as a service.                                              
touched = False
class MySubscriber:
    # It needs at least a callback to get ALMemory events.                                     
    def onTouched(key, value):
        global touched
        touched = True
        print("touched {}{}".format(key,value))
        pass

subscriber = MySubscriber()
# Register it with an arbitrary name.                                                          
service_name = "MySubscriber"
app.session.registerService(service_name, subscriber)

# Subscribe and tell exactly which service and method to call back.                            
memory_service.subscribeToEvent("TouchChanged", service_name, "onTouched")
