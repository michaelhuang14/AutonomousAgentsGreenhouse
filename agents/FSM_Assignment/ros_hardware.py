from hardware import *
import rospy
import sys, os
from std_msgs.msg import Float32, Int32, Int32MultiArray, Float32MultiArray, Bool, String
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/../lib")
from terrabot_utils import time_since_midnight

#sensor data passed as a file
class ROSSensors(Sensors):

    light_level = 0
    temperature = 0
    humidity = 0
    moisture = 0
    wlevel = 0
    light_level_raw = [0, 0]
    temperature_raw = [0, 0]
    humidity_raw = [0, 0]
    moisture_raw = [0, 0]
    wlevel_raw = 0

    def __init__(self):
        rospy.Subscriber('light_output', Int32MultiArray, self.light_callback)
        rospy.Subscriber('temp_output', Int32MultiArray, self.temp_callback)
        rospy.Subscriber('humid_output', Int32MultiArray, self.humid_callback)
        rospy.Subscriber('smoist_output', Int32MultiArray, self.moist_callback)
        rospy.Subscriber('level_output', Float32, self.level_callback)

    #your handlers here

    def getTime(self):
        return rospy.get_time()

    def light_callback(self, data):
        self.light_level = sum(data.data)/2.0
        self.light_level_raw = data.data

    def temp_callback(self, data):
        self.temperature = sum(data.data)/2.0
        self.temperature_raw = data.data

    def humid_callback(self, data):
        self.humidity = sum(data.data)/2.0
        self.humidity_raw = data.data

    def moist_callback(self, data):
        self.moisture = sum(data.data)/2.0
        self.moisture_raw = data.data

    def level_callback(self, data):
        self.wlevel = data.data
        self.wlevel_raw = data.data

    def doSense(self):
        #update the dictionary to return your values
        return {"unix_time":rospy.get_time(),
                "midnight_time":time_since_midnight(rospy.get_time()),
                "light": self.light_level,
                "temp":self.temperature, "humid":self.humidity,
                "smoist":self.moisture, "level":self.wlevel,
                "light_raw": self.light_level_raw,
                "temp_raw":self.temperature_raw, "humid_raw":self.humidity_raw,
                "smoist_raw":self.moisture_raw, "level_raw":self.wlevel_raw}

#actuators commanded as a file
class ROSActuators(Actuators):

    actuators = {}

    def __init__(self):
        self.actuators['led'] = rospy.Publisher('led_input', Int32,
                                                latch=True, queue_size=1)
        self.actuators['fan'] = rospy.Publisher('fan_input', Bool,
                                                latch=True, queue_size=1)
        self.actuators['wpump'] = rospy.Publisher('wpump_input', Bool,
                                                  latch=True, queue_size=1)
        self.actuators['ping'] = rospy.Publisher('ping', Bool,
                                                  latch=True, queue_size=1)
        self.actuators['camera'] = rospy.Publisher('camera', String,
                                                  latch=True, queue_size=1)

    def doActions(self, actions_tuple):
        actions = actions_tuple[2]
        #print(actions)
        for action in actions:
            self.actuators[action].publish(actions[action])

if __name__ == '__main__':
    rospy.set_param('use_sim_time', True)
    rospy.init_node('greenhouseagent', anonymous = True)
    sensors = ROSSensors()
    actuators = ROSActuators()
    actuators.doActions(('test', 0, {'fan' : True, 'wpump' : True, 'led' : 200}))
    while not rospy.core.is_shutdown():
        print(sensors.doSense())
        rospy.sleep(1)