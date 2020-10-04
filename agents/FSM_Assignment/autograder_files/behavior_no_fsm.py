
'''
Defines a general behavior.
Each behavior needs to be able to take in sensor and actuators
Each behavior must implement:
     perceive - to take in sensor data and time and output percepts
     plan - to take in percepts, determine new state
     act - to take in the state and output actions for each actuator
     start - to start up after running
     pause - to shut down before stopping
Each behavior performs one perceive, plan, act loop and returns the desired actions
doStep sends commands to actuators
'''
class Behavior(object):
    def __init__(self, name):
        self.name = name
        self.default = "perfect"
        self.isenabled = False
        self.state = self.default

    def setSensors(self, sensors):
        self.sensors = sensors

    def setActuators(self, actuators):
        self.actuators = actuators

    def perceive(self):
        pass

    def act(self):
        self.actuators.doActions((self.name, 0, {}))

    def start(self):
        self.isenabled = True

    def stop(self):
        self.state = self.default
        self.turnOffActuator()
        self.isenabled = False

    def turnOffActuator(self):
        pass

    def doStep(self):
        if self.isenabled:
            self.sensordata = self.sensors.doSense()
            self.perceive()
            self.act()


