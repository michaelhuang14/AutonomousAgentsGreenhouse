from transitions import Machine
from behavior import *
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from limits import *
from collections import deque as dq
from datetime import datetime

# sensor data passed into greenhouse behaviors:
#  [unix_time, midnight_time, light, temp, humid, smoist, level]
# actuators are looking for a dictionary with any/all of these keywords:
#  {"led":val, "fan":True/False, "wpump": True/False}


'''
The combined ambient and LED light level between 8am and 10pm should be 
between limit["light_level"]; between 10pm and 8am, the LEDs should be off (set to 0).
'''


class Light(Behavior):

    def __init__(self):
        super(Light, self).__init__("LightBehavior")
        # your initialization here
        self.states = ["nighttime", "daytime-low", "daytime-high", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]
        self.lightpower = 0

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "nighttime",
                                after="turnOff")  # , conditions=["is_nighttime"], after="turnOff")
        # self.fsm.add_transition("startbehav", "BehavOff", "daytime-low", conditions=["is_daytime_and_low"], after="addPower")
        # self.fsm.add_transition("startbehav", "BehavOff", "daytime-high", conditions=["is_daytime_and_high"], after="lowerPower")

        self.fsm.add_transition("stopbehav", "nighttime", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "daytime-low", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "daytime-high", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "daytime-low", "nighttime", conditions=["is_nighttime"], after="turnOff")
        self.fsm.add_transition("fsmStep", "daytime-high", "nighttime", conditions=["is_nighttime"], after="turnOff")

        self.fsm.add_transition("fsmStep", "nighttime", "daytime-low", conditions=["is_daytime_and_low"],
                                after="addPower")
        self.fsm.add_transition("fsmStep", "nighttime", "daytime-high", conditions=["is_daytime_and_high"],
                                after="lowerPower")
        self.fsm.add_transition("fsmStep", "daytime-high", "daytime-low", conditions=["is_daytime_and_low"],
                                after="addPower")
        self.fsm.add_transition("fsmStep", "daytime-low", "daytime-high", conditions=["is_daytime_and_high"],
                                after="lowerPower")
        self.fsm.add_transition("fsmStep", "daytime-high", "daytime-high", conditions=["is_daytime_and_high"],
                                after="lowerPower")
        self.fsm.add_transition("fsmStep", "daytime-low", "daytime-low", conditions=["is_daytime_and_low"],
                                after="addPower")

    def perceive(self):
        self.percept = (self.sensordata["midnight_time"], self.sensordata["light"])

    def act(self):
        # your code here
        self.fsmStep()

    def turnOffActuator(self):
        self.lightpower = 0
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": 0}))

    # your conditions here
    def is_nighttime(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t // 3600) % 24
        if not (hour >= 8 and hour < 22):
            # print("light-nighttime")
            return True
        return False

    def turnOff(self):
        self.lightpower = 0
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": 0}))

    def addPower(self):
        self.lightpower += 20
        self.lightpower = max(0, min(self.lightpower, 255))
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": self.lightpower}))

    def lowerPower(self):
        self.lightpower -= 20
        self.lightpower = max(0, min(self.lightpower, 255))
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": self.lightpower}))

    def is_daytime_and_low(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t // 3600) % 24
        if hour >= 8 and hour < 22 and lightlevel < limits['light_level'][0]:
            # print("light-daytime-low")
            return True
        return False

    def is_daytime_and_high(self):
        (midnight_t, lightlevel) = self.percept
        hour = (midnight_t // 3600) % 24
        if hour >= 8 and hour < 22 and lightlevel >= limits['light_level'][1]:
            # print("light-daytime-high")
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
        super(RaiseTemp, self).__init__("RaiseTempBehavior")  # Behavior sets reasonable defaults
        # your initialization here
        self.states = ["toolow", "perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")  # , conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("startbehav", "BehavOff", "toolow", conditions=["below_limit"], after="turnOn")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toolow", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "toolow", "perfect", conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toolow", conditions=["below_limit"], after="turnOn")
        # self.fsm.add_transition("fsmStep", "toolow", "toolow", conditions=["below_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["temp"])

    def act(self):
        # your code here
        self.fsmStep()

    # your conditions here
    def below_limit(self):
        (temp) = self.percept
        if temp < limits['temperature'][0]:
            # print("temp-low")
            return True
        return False

    def within_opt(self):
        (temp) = self.percept
        if temp >= optimal['temperature'][0]:
            # print("temp-withinopt")
            return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": 200}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": 0}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": 0}))

    def start(self):

        self.startbehav()

    def stop(self):
        self.stopbehav()


'''
The temperature should be below limit["temperature"].
'''


class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior")  # Behavior sets reasonable defaults
        # your initialization here
        self.states = ["toohigh", "perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")  # , conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("startbehav", "BehavOff", "perfect", conditions=["above_limit"],after="turnOn")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        # self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["temp"])

    def act(self):
        # your code here
        # print("lowertemp-" + str(self.sensordata["midnight_time"]//60) + " " + self.state)
        self.fsmStep()
        # print(self.state)

    # your conditions here
    def above_limit(self):
        (temp) = self.percept
        # print(str(temp) + " " + str(limits['temperature'][1]))
        if temp >= limits['temperature'][1]:
            # print("temp-high")
            return True
        return False

    def within_opt(self):
        (temp) = self.percept
        # print("check opt")
        if temp <= optimal['temperature'][1]:
            # print("temp-withinopt")
            return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def start(self):
        # self.sensordata = self.sensors.doSense()
        # self.perceive()
        # print("lowertemp-" + str(self.sensordata["midnight_time"]//60) + " " + self.state)
        self.startbehav()

    def stop(self):
        self.stopbehav()


'''
Humidity should be less than limit["humidity"]. 
'''


class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior")  # Behavior sets reasonable defaults
        # your initialization here
        self.states = ["toohigh", "perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        # self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["humid"])

    def act(self):
        # your code here
        self.fsmStep()

    # your conditions here
    def above_limit(self):
        (humid) = self.percept
        if humid >= limits['humidity'][1]:
            # print("humid-high")
            return True
        return False

    def within_opt(self):
        (humid) = self.percept
        if humid <= optimal['humidity'][1]:
            # print("humid-withinopt")
            return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def start(self):
        self.startbehav()

    def stop(self):
        self.stopbehav()


'''
Soil moisture should be above limits["moisture"]
'''


class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior")  # Behavior sets reasonable defaults
        # your initialization here
        self.states = ['ready', 'pump_on', 'pump_off', 'test_level', 'test_moist', 'BehavOff']
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)

        # startbehav transition
        self.fsm.add_transition("startbehav", "BehavOff", "ready")

        # stopbehav transitions
        self.fsm.add_transition("stopbehav", "ready", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "pump_on", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "pump_off", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "test_level", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "test_moist", "BehavOff", after="turnOffActuator")

        # fsmStep transitions
        # ready -> pump_on
        self.fsm.add_transition("fsmStep", "ready", "pump_on", conditions=["moist0_under_limit"],
                                unless=["enough_today"], after="save_level_pump_on")
        # pump_on -> pump_off
        self.fsm.add_transition("fsmStep", "pump_on", "pump_off", conditions=["timer_10_done"], after="pump_off")
        # pump_off -> test_moisture
        self.fsm.add_transition("fsmStep", "pump_off", "test_level", conditions=["timer_30_done"], after="update_today")
        # test_level -> ready OR test_moisture
        self.fsm.add_transition("fsmStep", "test_level", "ready", conditions=["enough_today"])
        self.fsm.add_transition("fsmStep", "test_level", "test_moist", conditions=["timer_300_done"],
                                unless=["enough_today"])
        # test moisture -> pump_on OR ready
        self.fsm.add_transition("fsmStep", "test_moist", "pump_on", conditions=["moist1_under_opt"],
                                after="save_level_pump_on")
        self.fsm.add_transition("fsmStep", "test_moist", "ready", unless=["moist1_under_opt"])

        # variables
        self.last_updated = 0  # last time self.today was reset
        self.today = 0  # how much water has been watered today
        self.est_moist0 = dq()  # sliding window (queue) for moist[0]
        self.est_moist1 = dq()  # sliding window (queue) for moist[1]
        self.est_level = dq()  # sliding window (queue) for water level
        self.start_level = 0  # starting level recorded before pump is turned on

    def perceive(self):
        (t, raw_soil, raw_level) = (self.sensordata["unix_time"], self.sensordata["smoist_raw"], self.sensordata["level"])
        # remove oldest entry in sliding window if window is full
        if len(self.est_moist0) == 300:
            self.est_moist0.pop()  # pops from right
        if len(self.est_moist1) == 300:
            self.est_moist1.pop()  # pops from right
        if len(self.est_level) == 5:
            self.est_level.pop()  # pops from right

        # add new entry to sliding window
        self.est_moist0.appendleft(raw_soil[0])
        self.est_moist1.appendleft(raw_soil[1])
        self.est_level.appendleft(raw_level)

        # calculate average of sliding window values
        moist0 = sum(self.est_moist0) / len(self.est_moist0)
        moist1 = sum(self.est_moist1) / len(self.est_moist1)
        level = sum(self.est_level) / len(self.est_level)

        self.percept = (t, [moist0, moist1], level)

    def act(self):
        # your code here
        (t, soil, level) = self.percept

        # reset at the start of each new day
        if t - self.last_updated >= 24 * 60 * 60:
            print(datetime.fromtimestamp(t).strftime("%D %H:%M:%S") + " Resetting self.today")
            self.today = 0  # reset
            self.last_updated = t  # reset

        self.fsmStep()

    # conditions
    def moist0_under_limit(self):
        (t, soil, level) = self.percept
        return soil[0] < limits['moisture'][0]

    def timer_10_done(self):
        (t, soil, level) = self.percept
        return t - self.timer_10 >= 10

    def timer_30_done(self):
        (t, soil, level) = self.percept
        return t - self.timer_30 >= 30

    def enough_today(self):
        return self.today >= 4.5

    def timer_300_done(self):
        (t, soil, level) = self.percept
        t - self.timer_300 >= 300

    def moist1_under_opt(self):
        (t, soil, level) = self.percept
        return soil[1] < optimal['moisture'][0]

    # actions
    def save_level_pump_on(self):
        (t, soil, level) = self.percept
        print(datetime.fromtimestamp(t).strftime("%D %H:%M:%S") + " Turning pump on")
        # saving water level
        self.start_level = level
        # turning pump on
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump": True}))
        # starting 10 second timer
        self.timer_10 = t

    def pump_off(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump": False}))
        # starting 30 second timer
        (t, soil, level) = self.percept
        print(datetime.fromtimestamp(t).strftime("%D %H:%M:%S") + " Turning pump off")
        self.timer_30 = t

    def update_today(self):
        (t, soil, level) = self.percept
        self.today += (self.start_level - level)
        # starting 5 min timer
        self.timer_300 = t

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"wpump": False}))

    def start(self):
        self.startbehav()

    def stop(self):
        self.stopbehav()


'''
Soil moisture should be lower than limits["moisture"]
'''


class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior")  # Behavior sets reasonable defaults
        # your initialization here
        self.states = ["toohigh", "perfect", "BehavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]

        self.fsm = Machine(model=self, states=self.states, initial='BehavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("startbehav", "BehavOff", "perfect")  # , after="turnOff")
        self.fsm.add_transition("stopbehav", "perfect", "BehavOff", after="turnOffActuator")
        self.fsm.add_transition("stopbehav", "toohigh", "BehavOff", after="turnOffActuator")

        self.fsm.add_transition("fsmStep", "toohigh", "perfect", conditions=["within_opt"], after="turnOff")
        # self.fsm.add_transition("fsmStep", "perfect", "perfect", conditions=["within_opt"], after="turnOff")

        self.fsm.add_transition("fsmStep", "perfect", "toohigh", conditions=["above_limit"], after="turnOn")
        # self.fsm.add_transition("fsmStep", "toohigh", "toohigh", conditions=["above_limit"], after="turnOn")

    def perceive(self):
        self.percept = (self.sensordata["smoist"])

    def act(self):
        # your code here
        self.fsmStep()

    # your conditions here
    def above_limit(self):
        (smoist) = self.percept
        if smoist > limits['moisture'][1]:
            # print("moist-high")
            return True
        return False

    def within_opt(self):
        (smoist) = self.percept
        if smoist <= optimal['moisture'][1]:
            # print("moist-withinopt")
            return True
        return False

    def turnOn(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": True}))

    def turnOff(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def turnOffActuator(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"fan": False}))

    def start(self):
        self.startbehav()

    def stop(self):
        self.stopbehav()