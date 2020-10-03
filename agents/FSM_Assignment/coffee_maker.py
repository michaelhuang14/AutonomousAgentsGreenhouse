from transitions import Machine
import logging
import datetime, time

class CoffeeMaker:

    def __init__(self):
        # names of states and actions must be identical in order to be graded accurately
        self.states = ["empty","pod", "size", "ready","heat", "disp", "enddisp"]
        self.actions = ["doStep"]
        self.sensordata = {"podpresent":False,"smallbuttonpressed":False, "medbuttonpressed":False, "largebuttonpressed":False, "startbuttonpressed": False, "watertemp":65}
        self.size = None
        #assumes logging is initialized already
        logging.getLogger('transitions').setLevel(logging.INFO)
        self.actionlogger = logging.getLogger('actions')
        self.actionlogger.setLevel(logging.INFO)
        self.sensorlogger = logging.getLogger('actions')
        self.sensorlogger.setLevel(logging.INFO)

        # Initialize the state machine
	self.fsm = Machine(model=self, states=self.states, initial='empty', ignore_invalid_triggers=True)
         #your code here
	self.fsm.add_transition("doStep", "empty", "pod", conditions=["podAdded"])
	self.fsm.add_transition("doStep", "pod", "empty", conditions=["podRemoved"])
	
        self.fsm.add_transition("doStep", "empty", "size", conditions=["sizeselect"], after="set_size")
	self.fsm.add_transition("doStep", "size", "size", conditions=["sizeselect"], after="set_size")
          
        self.fsm.add_transition("doStep", "size", "ready", conditions=["podAdded"])
	self.fsm.add_transition("doStep", "ready", "size", conditions=["podRemoved"])
        self.fsm.add_transition("doStep", "ready", "ready", conditions=["sizeselect"], after="set_size")
	self.fsm.add_transition("doStep", "pod", "ready", conditions=["sizeselect"], after="set_size")

	self.fsm.add_transition("doStep", "ready", "heat", conditions=["startPressed"], after="start_heating")
	self.fsm.add_transition("doStep", "heat", "disp", conditions=["tempReached"], after="start_dispensing")              
	self.fsm.add_transition("doStep", "disp", "enddisp", conditions=["timerdone"], after="done_dispensing")
	self.fsm.add_transition("doStep", "enddisp", "empty", conditions=["podRemoved"])

#your condition functions here
    def set_size(self):
        if self.sensordata["smallbuttonpressed"]:
            self.size = 1
        elif self.sensordata["medbuttonpressed"]:
            self.size = 2
        elif self.sensordata["largebuttonpressed"]:
            self.size = 3

    def timerdone(self):
        time = datetime.datetime.now()#int(str(datetime.datetime.now().time()).split(":")[2].split(".")[0])
        #print(str(time) + " " + str(self.start_disp_time))
        return (time - self.start_disp_time).seconds >= self.size * 5
           
    def tempReached(self):
        temp = self.sensordata["watertemp"]
        return temp >=180
   
    def startPressed(self):
        return self.sensordata["startbuttonpressed"]
        
    def sizeselect(self):
        if self.sensordata["smallbuttonpressed"] and self.size != 1:
            return True
        elif self.sensordata["medbuttonpressed"] and self.size != 2:
            return True
        elif self.sensordata["largebuttonpressed"] and self.size !=3:
            return True
        return False
    
    def podRemoved(self):
        return not self.sensordata["podpresent"]

    def podAdded(self):
        return self.sensordata["podpresent"]

    def start_heating(self):
        self.publish("START HEATING")

    def start_dispensing(self):
        #after publishing this message,
        #your code to dispense for a certain amount of time
        self.start_disp_time = datetime.datetime.now() #int(str(datetime.datetime.now().time()).split(":")[2].split(".")[0]) 
        #hint: use sensordata instead of spinning
        self.publish("START DISPENSING")

    def done_dispensing(self):
        self.publish("DONE DISPENSING")

    def sense(self, sensordata):
        #in case you want to store more data in self.sensordata,
        #we only write over the data that is sensed externally
        for sensor, data in sensordata.items():
            self.sensordata[sensor] = data
        self.sensorlogger.info(self.sensordata)

    def act(self):
        self.doStep()

    def publish(self, message):
        self.actionlogger.info(str(datetime.datetime.now())+","+message)

