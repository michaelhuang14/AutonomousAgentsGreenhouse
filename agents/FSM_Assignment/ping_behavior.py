from behavior import *
from transitions import Machine

'''
The behavior should ping once every 2-3 minutes
'''
class Ping(Behavior):

    def __init__(self):
        super(Ping, self).__init__("PingBehavior")
        #your code here
        self.time = 0
        self.states = ["waitforping", "behavOff"]
        self.actions = ["fsmStep", "startbehav", "stopbehav"]
        self.lightpower = 0

        self.fsm = Machine(model=self, states=self.states, initial='behavOff', ignore_invalid_triggers=True)
        self.fsm.add_transition("fsmStep", "waitforping", "waitforping", conditions=["timerdone"], after="publishping")
        self.fsm.add_transition("startbehav", "behavOff", "waitforping")
        self.fsm.add_transition("stopbehav", "waitforping", "behavOff")

    def perceive(self):
        self.current_time = self.sensordata["unix_time"]

    def start(self):
        #your code here
        self.startbehav()

    def stop(self):
        #your code here
        self.stopbehav()
    #your condition functions here

    def act(self):
        #your act function here
        self.fsmStep()

    def timerdone(self):
        cur_time = self.current_time
        if cur_time - self.time >= 120 or self.time == 0:
            return True
        return False
    
    def start(self):
        self.startbehav()

    def stop(self):
        self.stopbehav()
 
    def publishping(self):
        self.actuators.doActions((self.name, self.sensors.getTime(), {"ping":True}))
        self.time = self.current_time
