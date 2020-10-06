from behavior import *
from transitions import Machine
from vision import classifyFoliage, measureHeight
import sys, os.path as op
sys.path.append(op.dirname(op.dirname(op.abspath(__file__)))+"/../lib/")
from terrabot_utils import clock_time
import cv2
import datetime
from cv_utils import *

'''
The behavior should request an image when enabled, unless it is too dark.
It should check to be sure the image has been recorded and, if so, process
the image; if not, try again for up to 3 times before giving up
'''
class TakeImage(Behavior):

    def __init__(self):
        super(TakeImage, self).__init__("TakeImageBehavior")
        # Your code here
        self.states = ["stopState", "waitForImg", "acqImage"]
        self.actions = ["triggerStep", "triggerStart", "triggerStop"]

        self.imgInUse = ""
        self.numRetries = 0

        self.fsm = Machine(model=self, states=self.states, initial='stopState', ignore_invalid_triggers=True)

        self.fsm.add_transition(trigger='triggerStart', source='stopState', dest='acqImage',
                                conditions='is_img_avail')
        self.fsm.add_transition(trigger='triggerStop', source='waitForImg', dest='stopState',
                                after='refresh_vars')
        self.fsm.add_transition(trigger='triggerStop', source='acqImage', dest='stopState',
                                after='refresh_vars')


        self.fsm.add_transition(trigger='triggerStep', source='acqImage', dest='waitForImg',
                                conditions='is_enough_light', after='acquire_image')
        # self.fsm.add_transition(trigger='triggerStep', source='acqImage', dest='waitForImg',
        #                         conditions='is_enough_light', after='acquire_image')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='waitForImg',
                                conditions=['is_greater_10s', 'is_file_missing'], unless='is_done_3_retries', after='retry_acquire_image')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='stopState',
                                conditions=['is_greater_10s', 'is_file_missing', 'is_done_3_retries'],
                                after='print_warning')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='stopState',
                                conditions=['is_file_valid'], after='process_image')



    def is_img_avail(self):
        print("checking img avail")
        return (len(self.imgInUse) == 0)

    def is_enough_light(self):
        print("checking light avail, light: ", self.lightLev)
        return (self.lightLev > 20)

    def is_greater_10s(self):
        print("entering func: is_greater_10s")
        self.newTime = datetime.datetime.now()
        diff = (self.newTime - self.currTime).total_seconds()
        return (diff > 10)

    def is_file_missing(self):
        print("entering func: is_file_missing")
        return not(op.exists(self.imgInUse))

    def is_file_valid(self):
        return (op.exists(self.imgInUse))

    def is_done_3_retries(self):
        return (self.numRetries >= 3)

    def acquire_image(self):
        print("Entering func: acquire_image")
        (time_stringa, _, time_stringb) = str(self.time).partition('.')
        time_string = time_stringa + time_stringb + '.jpg'
        print("time string: ", time_string)


        path_name = '/home/robotanist/Desktop/Assign4/AutonomousAgentsGreenhouse/agents/camera_pics/camera_img' + time_string
        self.imgInUse = path_name
        self.currTime = datetime.datetime.now()
        self.actuators.doActions((self.name, self.sensors.getTime(), {"camera": path_name}))

    def retry_acquire_image(self):
        print("Entering func: retry_acquire_image")
        self.currTime = datetime.datetime.now()
        self.numRetries += 1
        print("Number of retries: ", self.numRetries)
        self.actuators.doActions((self.name, self.sensors.getTime(), {"camera": self.imgInUse}))

    def print_warning(self):
        print("Warning, 3 unsuccessful tries to capture image ", self.imgInUse)
        self.imgInUse = ""
        self.numRetries = 0

    def process_image(self):
        print("Entering func: proces_image")
        self.processImage(readImage(self.imgInUse))
        self.imgInUse = ""
        self.numRetries = 0

    def refresh_vars(self):
        print("Entering func: refresh_vars")
        self.imgInUse = ""
        self.numRetries = 0

    def perceive(self):
        self.time = self.sensordata['unix_time']
        # Your code here
        self.lightLev = self.sensordata['light']

    def act(self):
        # Your code here
        print("currState: ",self.state)
        self.triggerStep()

    def start(self):
        # Your code here
        self.triggerStart()

    def stop(self):
        # Your code here
        print("Stop trigger called")
        self.triggerStop()

    def processImage(self, image):
        foliage_mask = classifyFoliage(image)
        size = image.shape[0]*image.shape[1]
        percentage = cv2.countNonZero(foliage_mask)/size
        height = measureHeight(foliage_mask)
        print("As of %s, %.1f%% of pixels are foliage; plant height is %.1fcm"
             %(clock_time(self.time), 100*percentage,
                       (0 if not height else height)))
