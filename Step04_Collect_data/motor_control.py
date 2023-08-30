# Motor_Driver

import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
# LEFT		 | RIGHT
# LF(17, 27) | RF(9, 10)
# LR(22, 23) | RR)25, 24)
#		    RF ->  RR ->   LR  ->  LF
dcMotors = [9, 10, 25, 24, 22, 23, 17, 27]
wheels = []
MOT_FREQ = 1000
SPEED_MIN = 30
SPEED_MAX = 100

# Motor Output
forward = [True,False]
backward = [False,True]
STOP = [False,False]

def initMotor() :
	for i in range(0,len(dcMotors),2):
		GPIO.setup(dcMotors[i], GPIO.OUT)
		GPIO.output(dcMotors[i], False)

        # PWM dcMotors[1], [3], [5], [7]
		GPIO.setup(dcMotors[i+1], GPIO.OUT)
		wheel = GPIO.PWM(dcMotors[i+1], MOT_FREQ)
		wheel.start(0.0)
		wheels.append(wheel)

def goForward(spd) :
	if spd<0 : spd = 0
	spd += SPEED_MIN
	if spd>SPEED_MAX:
		spd = SPEED_MAX
	for i in range(0,len(dcMotors),2):
		GPIO.output(dcMotors[i], forward[i%2])
		wheels[i//2].ChangeDutyCycle(SPEED_MAX-spd)

def stopMotor() :
	for i in range(0,len(dcMotors),2):
		GPIO.output(dcMotors[i], STOP[i%2])
		wheels[i//2].ChangeDutyCycle(0.0)

def goBackward(spd) :
	if spd<0 : spd = 0
	spd = SPEED_MIN + spd + 15
	if spd>SPEED_MAX : spd = SPEED_MAX
	for i in range(0,len(dcMotors),2):
		GPIO.output(dcMotors[i], backward[i%2])
		wheels[i//2].ChangeDutyCycle(spd)

def turnLeft(spd) :
	if spd<0 : spd = 0
	spd += SPEED_MIN
	if spd>SPEED_MAX : spd = SPEED_MAX
	# RF, RR forward || LF, LR backward 
	for i in range(0, len(dcMotors)//2,2):
		GPIO.output(dcMotors[i], forward[i%2])
		wheels[i//2].ChangeDutyCycle(SPEED_MAX-spd-30)
	for i in range(len(dcMotors)//2, len(dcMotors),2):
		GPIO.output(dcMotors[i], backward[i%2])
		wheels[i//2].ChangeDutyCycle(spd+35)

def turnRight(spd) :
	if spd<0 : spd = 0
	spd += SPEED_MIN
	if spd>SPEED_MAX : spd = SPEED_MAX

	# LF, LR forward || RF, RR backward
	for i in range(0, len(dcMotors)//2, 2):
		GPIO.output(dcMotors[i], backward[i%2])
		wheels[i//2].ChangeDutyCycle(spd+35)
	for i in range(len(dcMotors)//2, len(dcMotors),2):
		GPIO.output(dcMotors[i], forward[i%2])
		wheels[i//2].ChangeDutyCycle(SPEED_MAX-spd-30)
	
def exitMotor() :
	for i in range(0,len(dcMotors),2):
		wheels[i//2].stop()
