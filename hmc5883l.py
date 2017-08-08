#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :

# HMC5888L Magnetometer (Digital Compass) wrapper class
# Based on https://bitbucket.org/thinkbowl/i2clibraries/src/14683feb0f96,
# but uses smbus rather than quick2wire and sets some different init
# params.

import smbus
import math
import time
import sys

class hmc5883l:

    __scales = {
        0.88: [0, 0.73],
        1.30: [1, 0.92],
        1.90: [2, 1.22],
        2.50: [3, 1.52],
        4.00: [4, 2.27],
        4.70: [5, 2.56],
        5.60: [6, 3.03],
        8.10: [7, 4.35],
    }

    def __init__(self, port=6, address=0x1E, gauss=1.3, declination=(0,0)):
        self.bus = smbus.SMBus(port)
        self.address = address

        (degrees, minutes) = declination
        self.__declDegrees = degrees
        self.__declMinutes = minutes
        self.__declination = (degrees + minutes / 60) * math.pi / 180

        self.calib_scale = {
            'x': 1,
            'y': 1,
            'z': 1
            }

        self.min_mag = {
            'x': 0,
            'y': 0,
            'z': 0
            }

        self.max_mag = {
            'x': 0,
            'y': 0,
            'z': 0
            }

        (reg, self.__scale) = self.__scales[gauss]
        self.bus.write_byte_data(self.address, 0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, 0x01,0xA0) # reg << 5) # Scale
        self.bus.write_byte_data(self.address, 0x02, 0x00) # Continuous measurement

    def declination(self):
        return (self.__declDegrees, self.__declMinutes)

    def twos_complement(self, val, len):
        # Convert twos compliment to integer
        if (val & (1 << len - 1)):
            val = val - (1<<len)
        return val

    def __convert(self, data, offset):
        val = self.twos_complement(data[offset] << 8 | data[offset+1], 16)
        if val == -4096: return None
        return round(val * self.__scale, 4)

    def axes(self):
        data = self.bus.read_i2c_block_data(self.address, 0x00,32)
        #print map(hex, data)
        #print(data)
        x = self.__convert(data, 3)
        y = self.__convert(data, 7)
        z = self.__convert(data, 5)

        x -= (self.min_mag['x'] + self.max_mag['x'])/2
        y -= (self.min_mag['y'] + self.max_mag['y'])/2
        z -= (self.min_mag['z'] + self.max_mag['z'])/2

        x *= self.calib_scale['x']
        y *= self.calib_scale['y']
        z *= self.calib_scale['z']

        return (x,y,z)

    def heading(self):
        x = 0
        y = 0
        z = 0
        iter = 1
        for i in range(500):
            try:
                (xi,yi,zi) = self.axes()
                x += xi
                y += yi
                z += zi
                iter += 1
            except:
                pass
        if iter > 1:
            iter -= 1
        x /= iter
        y /= iter
        z /= iter

        headingRad = math.atan2(x,y)
        headingRad += self.__declination

        # Correct for reversed heading
        if headingRad < 0:
            headingRad += 2 * math.pi

        # Check for wrap and compensate
        elif headingRad > 2 * math.pi:
            headingRad -= 2 * math.pi

        # Convert to degrees from radians
        headingDeg = headingRad * 180 / math.pi

        if headingDeg >=  180.0:
            headingDeg -= 180.0
        
        elif headingDeg < 180.0:
            headingDeg += 180.0

        return headingDeg

    def degrees(self, headingDeg):
        degrees = math.floor(headingDeg)
        minutes = round((headingDeg - degrees) * 60)
        return (degrees, minutes)

    def __str__(self):
        x,y,z = self.axes()

        d = 1
        h = self.degrees(self.heading())

        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \
               "Declination: " + str(d) + "\n" \
               "Heading: " + str(h) + "\n"

if __name__ == "__main__":
    # http://magnetic-declination.com/Great%20Britain%20(UK)/Harrogate#
    from calibrate import calibrate

    compass = hmc5883l(declination=(5,31))
    cal = calibrate()
    maxiter = 1000
    iter = 0
    second = 0
    print('Calibrate your compass')
    while iter < maxiter:
        iter += 1
        x,y,z = compass.axes()
        cal.getvals(x,y,z)

        second += 1
        if second == 100:
            print(iter/100)
            second = 0

    cal.calib_calc()
    compass.calib_scale = cal.scale
    compass.min_mag = cal.min
    compass.max_mag = cal.max

    while True:
        print(str(compass))
        
        sys.stdout.flush()
        time.sleep(0.5)

