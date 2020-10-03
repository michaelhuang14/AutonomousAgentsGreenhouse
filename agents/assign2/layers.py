import schedule as sched

class BehavioralLayer:

    def __init__(self,sensors, actuators, behaviorlist):
        #your code here
        self.behavior_list = {}
        self.started_behaviors = {}
        for behavior in behaviorlist:
            #print(behavior.name)
            behavior.setSensors(sensors) #there arent sensors specific to each behavior, but all sensors
            behavior.setActuators(actuators)
            self.behavior_list[behavior.name] = behavior
            self.started_behaviors[behavior.name] = False

    def startBehavior(self,name):
        #your code here
        if self.started_behaviors[name] is False: #stopped
            #print(name + " started")
            temp = self.behavior_list[name]
            temp.start()
            self.behavior_list[name] = temp
            self.started_behaviors[name] = True
        else:
            pass

    def stopBehavior(self,name):
        #your code here
        if  self.started_behaviors[name] is True: #started
            #print(name + " stopped")
            temp = self.behavior_list[name]
            temp.stop()
            self.behavior_list[name] = temp
            self.started_behaviors[name] = False
        else:
            pass

    def doStep(self):
        #your code here
        for (bname, beh)  in self.behavior_list.items():
            beh.doStep()


class ExecutiveLayer:

    def __init__(self):
        self.schedule = {}

    def setPlanningLayer(self, planning):
        self.planning = planning

    def setBehavioralLayer(self, behavioral):
        self.behavioral = behavioral

    def setSchedule(self, schedule):
        self.schedule = schedule # name -> (start, stop)

    def requestNewSchedule(self):
        self.planning.requestNewSchedule()

    def doStep(self, t): #t time in seconds
        #your code here
        curr_time = int(t//60) # time in minutes
        for (bname, intervals) in self.schedule.items():
            #print(bname + ":" + str(intervals))
            started = False
            for (start, stop) in intervals:
                started = (started or (start <= curr_time and curr_time < stop))
            if started:
                self.behavioral.startBehavior(bname)
            else:
                self.behavioral.stopBehavior(bname)
        #print(str(curr_time) + ":" + str(self.behavioral.started_behaviors))

class PlanningLayer:

    def __init__(self, schedulefile):
        self.schedulefile = schedulefile
        self.schedulerequested = True
        self.schedule = {}
        self.laststep = 0

    def setExecutive(self, executive):
        self.executive = executive

    def getNewSchedule(self):
        self.schedule = self.scheduleFromFile(self.schedulefile)
        self.executive.setSchedule(self.schedule)
        self.schedulerequested = False

    def requestNewSchedule(self):
        self.schedulerequested = True

    def doStep(self, t):
        if self.schedulerequested or self.checkEnded(t):
            self.getNewSchedule()
        self.laststep = (t//60)%(24*60)

    def checkEnded(self, t):
        mins = (t//60)%(24*60)
        if mins < self.laststep: #looped back around
            return True
        return False

    def scheduleFromFile(self, schedulefile):
        schedule = sched.readSchedule(schedulefile)
        return schedule
