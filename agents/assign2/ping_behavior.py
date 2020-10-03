from behavior import *

'''
The behavior should ping once every 2-3 minutes
'''
class Ping(Behavior):

    def __init__(self):
        super(Ping, self).__init__("PingBehavior")
        self.default = None #gets set when the behavior stops, not really needed
        #your code here

    def perceive(self):
        #your code here
        pass

    def act(self):
        #your code here
        pass
