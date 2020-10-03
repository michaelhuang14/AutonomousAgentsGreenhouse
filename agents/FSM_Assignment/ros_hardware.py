from hardware import *
import rospy
import sys, os
from std_msgs.msg import Float32, Int32, Int32MultiArray, Float32MultiArray, Bool, String

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/../lib")
from terrabot_utils import time_since_midnight

#sensor data passed as a file
class ROSSensors(Sensors):

    def __init__(self):
        #your code here
        self.light_level = 0
        self.temp_output = 0
        self.smoist_output = 0
        self.level_output = 0.0
        self.humid_output = 0
        rospy.Subscriber('light_output', Int32MultiArray, self.light_callback)
        rospy.Subscriber('temp_output', Int32MultiArray, self.temp_callback)
        rospy.Subscriber('smoist_output', Int32MultiArray, self.smoist_callback)
        rospy.Subscriber('humid_output', Int32MultiArray, self.humid_callback)
        rospy.Subscriber('level_output', Float32, self.level_callback)
    

    #your handlers here
    def light_callback(self, light_data):
        self.light_level = light_data.data[0]
    def temp_callback(self, temp_data):
        self.temp_output = temp_data.data[0]
    def smoist_callback(self, smoist_data):
        self.smoist_output = smoist_data.data[0]
    def humid_callback(self, humid_data):
        self.humid_output = humid_data.data[0]
    def level_callback(self, level_data):
        self.level_output = level_data.data
    
    def getTime(self):
        return rospy.get_time()

    def doSense(self):
        #update the dictionary to return your values
        return {"unix_time":rospy.get_time(), "midnight_time":time_since_midnight(rospy.get_time()), "light":self.light_level, "temp":self.temp_output, 
                "humid":self.humid_output, "smoist":self.smoist_output, "level":self.level_output}

#actuators commanded as a file
class ROSActuators(Actuators):

    def __init__(self):
        #your code here
        self.led_pub = rospy.Publisher('led_input', Int32, latch=True, queue_size=1)
        self.wpump_pub = rospy.Publisher('wpump_input', Bool, latch=True, queue_size=1)
        self.fan_pub = rospy.Publisher('fan_input', Bool, latch=True, queue_size=1)
        self.ping_pub = rospy.Publisher('ping', Bool, queue_size=1)

    def doActions(self, actions):
        #your code here
        (bname, time, act_dict) = actions 
        
        for (name, val) in act_dict.items():
            if name == "led":
                self.led_pub.publish(val)
            elif name == "wpump":
                self.wpump_pub.publish(val)
            elif name == "fan":
                self.fan_pub.publish(val)
            elif name == "ping":
                self.ping_pub.publish(val)



#####################################################
# Code to test your callbacks
#
# run TerraBot and python ros_hardware.py [-s] [-a]
# to test the sensors and actuators respectively
#####################################################
if __name__ == '__main__':
    rospy.set_param('use_sim_time', True)
    rospy.init_node('testrosagent', anonymous = True)
    sensors = ROSSensors()
    actuators = ROSActuators()
    acts = {'fan' : False, 'wpump' : False, 'led' : 0}
    while not rospy.core.is_shutdown():
        if "-s" in sys.argv:
            print(sensors.doSense())
        if "-a" in sys.argv:
            acts["fan"] = not acts["fan"]
            acts["wpump"] = not acts["wpump"]
            acts["led"] = 200-acts["led"]
            actuators.doActions(('test', 0, acts))
        rospy.sleep(2)
