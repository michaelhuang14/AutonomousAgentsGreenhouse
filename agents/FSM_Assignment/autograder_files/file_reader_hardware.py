from hardware import *
import csv

#sensor data passed as a file
class FileSensors(Sensors):

    def __init__(self,sensorfile):
        self.sensorfile = open(sensorfile, "r")
        self.sensordata = {}
        reader = csv.DictReader(self.sensorfile)
        self.dtime = 0
        for row in reader:
            values = {}
            for key in row:
                values[key] = int(row[key])
            # Assumes time points are evenly spaced and start at 0
            if (self.dtime == 0): self.dtime = values['time']
            self.sensordata[values["time"]] = values
            self.sensordata[values["time"]]["unix_time"] = self.sensordata[values["time"]]["time"]
            self.sensordata[values["time"]]["midnight_time"] = self.sensordata[values["time"]]["time"]
        self.sensorfile.close()
        self.time = 0

    def doSense(self):
        return self.sensordata[self.time]

    def incrementTime(self):
        self.time += self.dtime

    def getTime(self):
        return self.time

#actuators commanded as a file
class FileActuators(Actuators):

    def __init__(self,actuationfile):
        self.actfile = open(actuationfile,"w")

    def doActions(self, actions):
        self.actfile.write(str(actions)+"\n")

    def closeFile(self):
        self.actfile.close()
