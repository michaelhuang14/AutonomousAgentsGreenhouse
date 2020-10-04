from autograder_files.behavior_no_fsm import *
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from limits import *

#sensor data passed into greenhouse behaviors:
#  [time, lightlevel, temperature, humidity, soilmoisture, waterlevel]
#actuators are looking for a dictionary with any/all of these keywords:
#  {"led":val, "fan":True/False, "wpump": True/False}

'''
The behavior should ping once every 2-3 minutes
'''
class Ping(Behavior):

    def __init__(self):
        super(Ping, self).__init__("PingBehavior")
        self.default = None
        self.state = self.default

    def perceive(self):
        pass

    def act(self):
        if self.state == None or self.sensordata["unix_time"]-self.state >= 120:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"ping":True}))
            self.state = self.sensors.getTime()


'''
The combined ambient and LED light level between 8am and 10pm should be 
between 850-950; between 10pm and 8am, the LEDs should be off (set to 0).
Except when non-light behaviors need to be run...
'''
class Light(Behavior):

    def __init__(self):
        super(Light, self).__init__("LightBehavior")
        self.default = 0
        self.state = self.default #value for lights
    
    def perceive(self):
        self.percept = (self.sensordata["midnight_time"], self.sensordata["light"]) 
    
    def act(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t//3600)%24
        if hour >= 8 and hour < 22:
            if lightlevel < limits['light_level'][0]:
                self.state += 20
            elif lightlevel >= limits['light_level'][1]:
                self.state -= 20
            self.state = max(0,min(self.state,255))
        else:
            self.state = 0

        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":self.state}))
    
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
        
'''
The temperature should be greater than or equal to 22C.
'''
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior") #Behavior sets reasonable defaults
        #self.state = "perfect" or "toolow"
        
    def perceive(self):
        self.percept = (self.sensordata["temp"])

    def act(self):
        (temp) = self.percept
        if temp < limits['temperature'][0]:
            self.state = "toolow"
        elif temp >= optimal['temperature'][0]:
            self.state = "perfect"
            
        if self.state == "toolow":
            self.actuators.doActions((self.name, self.sensors.getTime(), {"led":200}))
        else:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
            
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
        
'''
The temperature should be less than 28C.
'''
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior") #Behavior sets reasonable defaults
        #self.state = "perfect" or "toohigh"
        
    def perceive(self):
        self.percept = (self.sensordata["temp"])

    def act(self):
        (temp) = self.percept
        if temp >= limits['temperature'][1]:
            self.state = "toohigh"
        elif temp <= optimal['temperature'][1]:
            self.state = "perfect"
            
        if self.state == "toohigh":
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True})) 
        else:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False})) 
            
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))

    
'''
Humidity should be less than 80%. 
'''
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior") #Behavior sets reasonable defaults
        #self.state = "perfect" or "toohumid"

    def perceive(self):
        self.percept = (self.sensordata["humid"])

    def act(self):
        (humid) = self.percept
        if humid >= limits['humidity'][1]:
            self.state = "toohumid"
        elif humid <=  optimal['humidity'][1]:
            self.state = "perfect"
            
        if self.state == "toohumid":
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True})) 
        else:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False})) 
            
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))
            

'''
Soil moisture should be in the range [500,650)
'''
class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior") #Behavior sets reasonable defaults
        self.state = "ready"
        self.default = "ready"
        #self.state = "watering", "soakingup", "ready"
    
    def perceive(self):
        self.percept = (self.sensordata["unix_time"], self.sensordata["smoist"], self.sensordata["level"]) 

    def act(self):
        (t,soil,water) = self.percept
        if self.state == "watering" and self.waterlevel - water > 0.5:
            self.state = "soakingup"
            self.waittime = t
        elif self.state == "soakingup" and t-self.waittime >= 5*60:
            self.state = "ready"
        elif self.state == "ready" and soil < limits['moisture'][0]:
            self.state = "watering"
            self.waterlevel = water

        if self.state == "watering":
            self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":True}))
        else:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":False}))
            
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":False}))
        
'''
Soil moisture should be in the range [500,650)
'''
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior") #Behavior sets reasonable defaults
        #self.state = "perfect" or "toomoist"
    
    def perceive(self):
        self.percept = (self.sensordata["smoist"])

    def act(self):
        (soil) = self.percept
        if soil >= limits['moisture'][1]:
            self.state = "toomoist"
        elif soil <= optimal['moisture'][1]:
            self.state = "perfect"
            
        if self.state == "toomoist":
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True}))
        else:
            self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))
            
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))


    

        
