from transitions import Machine
from behavior import *
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from limits import *

#sensor data passed into greenhouse behaviors:
#  [unix_time, midnight_time, light, temp, humid, smoist, level]
#actuators are looking for a dictionary with any/all of these keywords:
#  {"led":val, "fan":True/False, "wpump": True/False}
            

'''
The combined ambient and LED light level between 8am and 10pm should be 
between limit["light_level"]; between 10pm and 8am, the LEDs should be off (set to 0).
'''
class Light(Behavior):

    def __init__(self):
        super(Light, self).__init__("LightBehavior")
        #your initialization here
        self.states = ["nighttime","daytime-low", "daytime-high", "BehavOff"]
        self.actions = ["fsmStep","startbehav", "stopbehav"]
        self.lightpower = 0

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "nighttime", after="turnOff")#, conditions=["is_nighttime"], after="turnOff")
        #self.fsm.add_transition("startbehav", "BehavOff", "daytime-low", conditions=["is_daytime_and_low"], after="addPower")
        #self.fsm.add_transition("startbehav", "BehavOff", "daytime-high", conditions=["is_daytime_and_high"], after="lowerPower")

        self.fsm.add_transition("stopbehav", "nighttime", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "daytime-low", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "daytime-high", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "daytime-low", "nighttime", conditions=["is_nighttime"], after="turnOff")
        self.fsm.add_transition("fsmStep", "daytime-high", "nighttime", conditions=["is_nighttime"], after="turnOff")
 
        self.fsm.add_transition("fsmStep", "nighttime", "daytime-low", conditions=["is_daytime_and_low"], after="addPower")
        self.fsm.add_transition("fsmStep", "nighttime", "daytime-high", conditions=["is_daytime_and_high"], after="lowerPower")
        self.fsm.add_transition("fsmStep", "daytime-high", "daytime-low", conditions=["is_daytime_and_low"], after="addPower")
        self.fsm.add_transition("fsmStep", "daytime-low", "daytime-high", conditions=["is_daytime_and_high"], after="lowerPower")
        self.fsm.add_transition("fsmStep", "daytime-high", "daytime-high", conditions=["is_daytime_and_high"], after="lowerPower")          
        self.fsm.add_transition("fsmStep", "daytime-low", "daytime-low", conditions=["is_daytime_and_low"], after="addPower")


    def perceive(self):
        self.percept = (self.sensordata["midnight_time"], self.sensordata["light"]) 
    
    def act(self):
        #your code here
        self.fsmStep()

    def turnOffActuator(self):
        self.lightpower=0
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
        
    #your conditions here
    def is_nighttime(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t//3600)%24
        if not (hour >= 8 and hour < 22):
            #print("light-nighttime")
            return True
        return False

    def turnOff(self):
        self.lightpower = 0
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
  
    def addPower(self):
        self.lightpower += 20
        self.lightpower = max(0,min(self.lightpower,255))
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":self.lightpower}))
    def lowerPower(self):
        self.lightpower -= 20
        self.lightpower = max(0,min(self.lightpower,255))
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":self.lightpower}))

    def is_daytime_and_low(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t//3600)%24
        if hour >= 8 and hour < 22 and lightlevel < limits['light_level'][0]:
                #print("light-daytime-low")
                return True
        return False
        
    def is_daytime_and_high(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t//3600)%24
        if hour >= 8 and hour < 22 and lightlevel >= limits['light_level'][1]:
                #print("light-daytime-high")
                return True
        return False

    def start(self):
        self.startbehav()
    def stop(self):
        self.stopbehav()
'''
The temperature should be above limit["temperature"].
'''
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior") #Behavior sets reasonable defaults
        #your initialization here
        self.states = ["toolow","perfect","BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")#, conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("startbehav", "BehavOff", "toolow", conditions=["below_limit"], after="turnOn")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toolow", "BehavOff", after="turnOffActuator")


        self.fsm.add_transition("fsmStep", "toolow", "perfect", conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toolow", conditions=["below_limit"], after="turnOn")
        #self.fsm.add_transition("fsmStep", "toolow", "toolow", conditions=["below_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["temp"]) 

    def act(self):
        #your code here
        self.fsmStep()
        
    #your conditions here
    def below_limit(self):
        (temp) = self.percept
        if temp < limits['temperature'][0]:
           #print("temp-low") 
           return True
        return False

    def within_opt(self):
        (temp) = self.percept
        if temp >= optimal['temperature'][0]:
           #print("temp-withinopt")
           return True
        return False
    
    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":200}))
   
    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
        
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led":0}))
    def start(self):
        
        self.startbehav()
    def stop(self):
        self.stopbehav()
'''
The temperature should be below limit["temperature"].
'''
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior") #Behavior sets reasonable defaults
        #your initialization here
        self.states = ["toohigh","perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")#, conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("startbehav", "BehavOff", "perfect", conditions=["above_limit"],after="turnOn")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        #self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")
 
        
    def perceive(self):
        self.percept = (self.sensordata["temp"]) 

    def act(self):
        #your code here
        #print("lowertemp-" + str(self.sensordata["midnight_time"]//60) + " " + self.state)
        self.fsmStep()
        #print(self.state)
        
    #your conditions here
    def above_limit(self):
        (temp) = self.percept
        #print(str(temp) + " " + str(limits['temperature'][1]))
        if temp >= limits['temperature'][1]:
           #print("temp-high")
           return True
        return False

    def within_opt(self):
        (temp) = self.percept
        #print("check opt")
        if temp <= optimal['temperature'][1]:
           #print("temp-withinopt")
           return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))
    
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))
    def start(self):
        #self.sensordata = self.sensors.doSense()
        #self.perceive()
        #print("lowertemp-" + str(self.sensordata["midnight_time"]//60) + " " + self.state)
        self.startbehav()

    def stop(self):
        self.stopbehav()
'''
Humidity should be less than limit["humidity"]. 
'''
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior") #Behavior sets reasonable defaults
        #your initialization here
        self.states = ["toohigh","perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        #self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")
 

    def perceive(self):
        self.percept = (self.sensordata["humid"]) 
        
    def act(self):
        #your code here
        self.fsmStep()
        
    #your conditions here
    def above_limit(self):
        (humid) = self.percept
        if humid >= limits['humidity'][1]:
           #print("humid-high")
           return True
        return False

    def within_opt(self):
        (humid) = self.percept
        if humid <= optimal['humidity'][1]:
           #print("humid-withinopt")
           return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))
    def start(self):
        self.startbehav()
    def stop(self):
        self.stopbehav()
'''
Soil moisture should be above limits["moisture"]
'''
class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior") #Behavior sets reasonable defaults
        #your initialization here
        self.states = ["ready","watering", "soakingup", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "ready")#, after="turnOff")
        self.fsm.add_transition("stopbehav", "ready", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "watering", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "soakingup", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "ready", "watering", conditions=["soil_too_dry"], after="water")
        self.fsm.add_transition("fsmStep", "watering", "soakingup", conditions=["enough_water"], after="start_soaking")
        self.fsm.add_transition("fsmStep", "soakingup", "ready", conditions=["timerdone"], after="turnOff")

    def perceive(self):
        self.percept = (self.sensordata["unix_time"], self.sensordata["smoist"], self.sensordata["level"]) 
        
    def act(self):
        #your code here
        self.fsmStep()
        
    #your conditions here
    def soil_too_dry(self):
        (t,soil,water) = self.percept
        if soil < limits['moisture'][0]:
            #print("smoist-toodry")
            return True
        return False
    
    def water(self):
        #print("watering") 
        (t,soil,water) = self.percept
        self.waterlevel = water
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":True}))

    def enough_water(self):
        (t,soil,water) = self.percept
        if self.waterlevel - water > 0.5:
           #print("finished watering")
           return True
        return False
     
    def start_soaking(self):
        (t,soil,water) = self.percept
        self.waittime = t
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":False}))
   
    def timerdone(self):
        (t,soil,water) = self.percept
        if t-self.waittime >= 5*60:
            #print("soaking done") 
            return True
        return False
    
    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":False}))
 
    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump":False}))

    def start(self):
        self.startbehav()
    def stop(self):
        self.stopbehav()
'''
Soil moisture should be lower than limits["moisture"]
'''
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior") #Behavior sets reasonable defaults
        #your initialization here
        self.states = ["toohigh","perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")#, after="turnOff")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")


        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        #self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        #self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["smoist"]) 
        
    def act(self):
        #your code here
        self.fsmStep()
        
    #your conditions here
    def above_limit(self):
        (smoist) = self.percept
        if smoist > limits['moisture'][1]:
           #print("moist-high")
           return True
        return False

    def within_opt(self):
        (smoist) = self.percept
        if smoist <= optimal['moisture'][1]:
           #print("moist-withinopt")
           return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan":False}))

    def start(self):
        self.startbehav()
    def stop(self):
        self.stopbehav()
        
