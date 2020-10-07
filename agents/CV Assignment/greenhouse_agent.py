import rospy, ros_hardware, greenhouse_behaviors, ping_behavior, layers, camera_behavior

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/../lib")
from terrabot_utils import time_since_midnight

class LayeredGreenhouseAgent:

    def __init__(self,schedulefile):
        rospy.set_param('use_sim_time', True)
        rospy.init_node('greenhouseagent', anonymous = True)

        #your code from Assignment 1 plus Ping here
        self.sensors = ros_hardware.ROSSensors()
        self.actuators = ros_hardware.ROSActuators()
        self.ping_behavior = ping_behavior.Ping()
        self.camera_behavior = camera_behavior.TakeImage()
        behavior_list = [greenhouse_behaviors.Light(),greenhouse_behaviors.LowerHumid(), greenhouse_behaviors.RaiseTemp(), greenhouse_behaviors.LowerTemp()
            , greenhouse_behaviors.LowerSMoist(), greenhouse_behaviors.RaiseSMoist(), self.ping_behavior, self.camera_behavior]

        self.behavioral_layer = layers.BehavioralLayer(self.sensors, self.actuators, behavior_list)
        self.executive_layer = layers.ExecutiveLayer()
        self.planning_layer = layers.PlanningLayer(schedulefile)
        self.executive_layer.setBehavioralLayer(self.behavioral_layer)
        self.executive_layer.setPlanningLayer(self.planning_layer)
        self.executive_layer.requestNewSchedule()
        self.planning_layer.setExecutive(self.executive_layer)


    def main(self):
        rospy.sleep(2)
        while rospy.get_time() == 0: rospy.sleep(1)
        #your code here if necessary
        last_ping = rospy.get_time() 
        self.ping_behavior.act()
       
        while not rospy.core.is_shutdown():
            t = time_since_midnight(self.sensors.getTime())
            self.planning_layer.doStep(t)
            rospy.sleep(1)
            self.executive_layer.doStep(t)
            rospy.sleep(1)
            self.behavioral_layer.doStep()
            rospy.sleep(1)


if __name__ == '__main__':
    agent = LayeredGreenhouseAgent("greenhouse_schedule.txt")
    agent.main()

