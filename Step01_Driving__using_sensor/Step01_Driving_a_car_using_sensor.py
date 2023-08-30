# Driving a car with Reflective Optical Sensor(TCRT5000)
# 01. Receiving input value from sensor
# 02. Set function settings according to sensor input value
# 03. If left is 1, right turn is activated.
# 04. If right is 1, left turn is activated.
# 05. If left and right is 0, straight ahead.

import RPi.GPIO as GPIO
from motor_control import *
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
initMotor()
speedFwd = 0;
speedCurve = 0;

# Setting TCRT5000(sensor) input
DOs = [21,20]
for DO in DOs:
	GPIO.setup(DO, GPIO.IN)

# Exception handling with using Keyboard Interrupt
try:
	while True:
		# if the floor is black, the output is 1.
		right = GPIO.input(DOs[0])
		left  = GPIO.input(DOs[1])
		print("left: " , left, "Right:" , right)
		if not right and not left :
			goForward(speedFwd)
		elif not right and left :
			turnRight(speedCurve)
		elif right and not left :
			turnLeft(speedCurve)
except KeyboardInterrupt:
	pass

exitMotor()
GPIO.cleanup()
