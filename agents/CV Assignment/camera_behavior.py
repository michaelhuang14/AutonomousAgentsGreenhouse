from behavior import *
from transitions import Machine
from vision import classifyFoliage, measureHeight
import sys, os.path as op
sys.path.append(op.dirname(op.dirname(op.abspath(__file__)))+"/../lib/")
from terrabot_utils import clock_time
import cv2

'''
The behavior should request an image when enabled, unless it is too dark.
It should check to be sure the image has been recorded and, if so, process
the image; if not, try again for up to 3 times before giving up
'''
class TakeImage(Behavior):

    def __init__(self):
        super(TakeImage, self).__init__("TakeImageBehavior")
        # Your code here

    def perceive(self):
	self.time = self.sensordata['unix_time']
        # Your code here
        pass

    def act(self):
        # Your code here
        pass

    def start(self):
        # Your code here
        pass

    def stop(self):
        # Your code here
        pass

    def processImage(self, image):
	foliage_mask = classifyFoliage(image)
	size = image.shape[0]*image.shape[1]
	percentage = cv2.countNonZero(foliage_mask)/size
	height = measureHeight(foliage_mask)
	print("As of %s, %.1f%% of pixels are foliage; plant height is %.1fcm"
		 %(clock_time(self.time), 100*percentage,
                   (0 if not height else height)))
