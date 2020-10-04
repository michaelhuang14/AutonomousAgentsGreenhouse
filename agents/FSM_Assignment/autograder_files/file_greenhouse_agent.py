import greenhouse_behaviors, layers
from autograder_files import file_reader_hardware

class LayeredGreenhouseAgent:

    def __init__(self, sensorfile, schedulefile, outputfile, beh):
        self.sensors = file_reader_hardware.FileSensors(sensorfile)
        self.actuators = file_reader_hardware.FileActuators(outputfile)
        self.behaviorallayer = layers.BehavioralLayer(self.sensors, self.actuators, beh)
        self.executivelayer = layers.ExecutiveLayer()
        self.planninglayer = layers.PlanningLayer(schedulefile)
        self.planninglayer.setExecutive(self.executivelayer)
        self.executivelayer.setPlanningLayer(self.planninglayer)
        self.executivelayer.setBehavioralLayer(self.behaviorallayer)
        self.outputfile = outputfile

    def main(self):
        self.behaviorallayer.startBehavior("PingBehavior")
        while self.sensors.time < 24*3600:
            self.planninglayer.doStep(self.sensors.time)
            self.executivelayer.doStep(self.sensors.time)
            self.behaviorallayer.doStep()
            self.sensors.incrementTime()
        self.actuators.closeFile()


class BehavioralGreenhouseAgent:

    def __init__(self, sensorfile, outputfile, beh):
        self.sensors = file_reader_hardware.FileSensors(sensorfile)
        self.actuators = file_reader_hardware.FileActuators(outputfile)
        self.behaviorallayer = layers.BehavioralLayer(self.sensors, self.actuators, beh)
        for b in beh:
            self.behaviorallayer.startBehavior(b.name)
        self.outputfile = outputfile

    def main(self):
        while self.sensors.time < 24*3600:
            self.behaviorallayer.doStep()
            self.sensors.incrementTime()
        self.actuators.closeFile()