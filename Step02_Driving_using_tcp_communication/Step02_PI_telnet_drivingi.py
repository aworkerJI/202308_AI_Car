# Set PI as the socket communication server
# 01 Transmission to PC of infrared sensor values and camera data
# 02 Running a thread with data received from a PC

import socket
import struct
import cv2
import pickle
import RPi.GPIO as GPIO
import threading
from motor_control import *

GPIO.setmode(GPIO.BCM)	

initMotor()

# speed for 0~90
speedFwd = 0
speedCurve = 0

# Setting TCRT5000(sensor) input
DOs = [21,20]
for DO in DOs:
	GPIO.setup(DO, GPIO.IN)

VIDSRC = 'v4l2src device=/dev/video0 ! video/x-raw,width=160,height=120,framerate=20/1 ! videoscale ! videoconvert ! jpegenc ! appsink'
cap=cv2.VideoCapture(VIDSRC, cv2.CAP_GSTREAMER)

HOST = ''
# User-selectable PORT number 1024~65535
PORT = 3232

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Assign an address and PORT
server.bind((HOST, PORT))
print('Socket bind complete')

# Set the number of waiting queues
server.listen(10)
print('Socket now listening')

# Waiting for a connection request through a socket
server_cam, addr = server.accept()
server_mot, addr = server.accept()
print('New Client connection')

# Used to terminate a thread
flag_exit = False

# Thread to receive messages and operate motor's functions
# Running a thread with data received from a PC
def mot_main() :
	while True:
		# received a 1-byte message from PC
		rl_byte = server_mot.recv(1)
		rl = struct.unpack('!B', rl_byte)
		right, left = (rl[0] & 2)>>1, rl[0] & 1

		if not right and not left :
			goForward(speedFwd)
		elif not right and left :
			turnRight(speedCurve)
		elif right and not left :
			turnLeft(speedCurve)
		if flag_exit: break

motThread = threading.Thread(target=mot_main)
motThread.start()

try:
	while True:
		cmd_byte = server_cam.recv(1)
		cmd = struct.unpack('!B', cmd_byte)
		# print(cmd[0])
		if cmd[0]==32 :

			# capture sensor data
			right = GPIO.input(DOs[0])
			left  = GPIO.input(DOs[1])

			# capture camera data
			ret,frame=cap.read()

			# prepare sensor data 		
			rl = right<<1|left<<0
			rl_byte = struct.pack("!B", rl)
			
			# Serialize frame
			data = pickle.dumps(frame)
		
			# send sensor + camera data
			data_size = struct.pack("!L", len(data)) 
			server_cam.sendall(rl_byte + data_size + data)
			
except KeyboardInterrupt:
	pass
except ConnectionResetError:
	pass
except BrokenPipeError:
	pass
except:
	pass

flag_exit = True
motThread.join()

# Communication connection terminated
server_cam.close()
server_mot.close()
server.close()

exitMotor()
GPIO.cleanup()