import math
import time



class calibrate(object):
    
    def __init__(self):
        
        self.min = {
            'x': 1000000,
            'y': 1000000,
            'z': 1000000
        }

        self.max = {
            'x': -1000000,
            'y': -1000000,
            'z': -1000000
        }


    def getvals(self,x,y,z):

            self.min['x'] = min(self.min['x'],x)
            self.min['y'] = min(self.min['y'],y)
            self.min['z'] = min(self.min['z'],z)

            self.max['x'] = max(self.max['x'],x)
            self.max['y'] = max(self.max['y'],y)
            self.max['z'] = max(self.max['z'],z)

            time.sleep(.01)


    def calib_calc(self):
        varymax = {
            'x': self.max['x'] - ((self.min['x'] + self.max['x'])/2),
            'y': self.max['y'] - ((self.min['y'] + self.max['y'])/2),
            'z': self.max['z'] - ((self.min['z'] + self.max['z'])/2)
        }

        varymin = {
            'x': self.min['x'] - ((self.min['x'] + self.max['x'])/2),
            'y': self.min['y'] - ((self.min['y'] + self.max['y'])/2),
            'z': self.min['z'] - ((self.min['z'] + self.max['z'])/2)
        }

        avg = {
            'x': (varymax['x'] - varymin['x'])/2,
            'y': (varymax['y'] - varymin['y'])/2,
            'z': (varymax['z'] - varymin['z'])/2
        }

        avgrad = (avg['x'] + avg['y'] + avg['z'])/3

        self.scale = {
            'x': avgrad/avg['x'],
            'y': avgrad/avg['y'],
            'z': avgrad/avg['z']
        }


