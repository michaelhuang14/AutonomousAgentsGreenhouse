from behavior import *
from transitions import Machine
from vision import classifyFoliage, measureHeight
import sys, os.path as op
sys.path.append(op.dirname(op.dirname(op.abspath(__file__)))+"/../lib/")
from terrabot_utils import clock_time
import cv2
import datetime, time

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
                                conditions='refresh_vars')
        self.fsm.add_transition(trigger='triggerStop', source='acqImage', dest='stopState',
                                conditions='refresh_vars')


        self.fsm.add_transition(trigger='triggerStep', source='acqImage', dest='waitForImg',
                                conditions='is_enough_light', after='acquire_image')
        self.fsm.add_transition(trigger='triggerStep', source='acqImage', dest='waitForImg',
                                conditions='is_enough_light', after='acquire_image')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='waitForImg',
                                conditions=['is_greater_10s', 'is_file_missing'], after='retry_acquire_image')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='stopState',
                                conditions=['is_greater_10s', 'is_file_missing', 'is_done_3_retries'],
                                after='print_warning')
        self.fsm.add_transition(trigger='triggerStep', source='waitForImg', dest='stopState',
                                conditions=['is_file_valid'], after='process_image')



    def is_img_avail(self):
        return (len(self.imgInUse) == 0)

    def is_enough_light(self):
        return (self.lightLev > 20)

    def is_greater_10s(self):
        self.newTime = datetime.datetime.now()
        diff = (self.currTime - self.newTime).total_seconds()
        return (diff > 10)

    def is_file_missing(self):
        return not(op.exists(self.imgInUse))

    def is_done_3_retries(self):
        return (self.numRetries >= 3)

    def acquire_image(self):
        path_name = '~/camera_img' + str(self.time)
        self.imgInUse = path_name
        self.currTime = datetime.datetime.now()
        self.actuators.doActions((self.name, self.sensors.getTime(), {"camera": path_name}))

    def retry_acquire_image(self):
        self.currTime = datetime.datetime.now()
        self.numRetries += 1
        self.actuators.doActions((self.name, self.sensors.getTime(), {"camera": self.imgInUse}))

    def print_warning(self):
        print("Warning, 3 unsuccessful tries to capture image ", self.imgInUse)
        self.imgInUse = ""
        self.numRetries = 0

    def process_image(self):
        self.processImage(self.imgInUse)
        self.imgInUse = ""
        self.numRetries = 0

    def refresh_vars(self):
        self.imgInUse = ""
        self.numRetries = 0

    def perceive(self):
        self.time = self.sensordata['unix_time']
        # Your code here
        self.lightLev = self.sensordata['light']

    def act(self):
        # Your code here
        self.triggerStep()

    def start(self):
        # Your code here
        self.triggerStart()

    def stop(self):
        # Your code here
        self.triggerStop()

    def processImage(self, image):
        foliage_mask = classifyFoliage(image)
        size = image.shape[0]*image.shape[1]
        percentage = cv2.countNonZero(foliage_mask)/size
        height = measureHeight(foliage_mask)
        print("As of %s, %.1f%% of pixels are foliage; plant height is %.1fcm"
             %(clock_time(self.time), 100*percentage,
                       (0 if not height else height)))
