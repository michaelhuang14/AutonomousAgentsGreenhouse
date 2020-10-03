from hardware import *
import csv

#sensor data passed as a file
class FileSensors(Sensors):

    def __init__(self,sensorfile):
        self.sensorfile = open(sensorfile, "r")
        self.sensordata = {}
        reader = csv.DictReader(self.sensorfile)
        for row in reader:
            values = {}
            for key in row:
                values[key] = int(row[key])
            self.sensordata[values["time"]] = values
        self.sensorfile.close()
        self.time = 0

    def doSense(self):
        return self.sensordata[self.time]

    def incrementTime(self):
        self.time += 3600

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
