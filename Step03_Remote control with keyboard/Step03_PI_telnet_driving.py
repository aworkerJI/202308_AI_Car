# Set PI as the socket communication server
# 01 Transmission to PC of camera data
# 02 Running a remote control thread with data received from a PC

import socket
import struct
import cv2
import pickle
import RPi.GPIO as GPIO
import threading
from motor_control import *

GPIO.setmode(GPIO.BCM)
initMotor()
	
speedFwd = 0 
speedCurve = 0 

VIDSRC = 'v4l2src device=/dev/video0 ! video/x-raw,width=160,height=120,framerate=20/1 ! videoscale ! videoconvert ! jpegenc ! appsink'

cap=cv2.VideoCapture(VIDSRC, cv2.CAP_GSTREAMER)

HOST = ''
PORT = 3232

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

server.bind((HOST, PORT))
print('Socket bind complete')

server.listen(10)
print('Socket now listening')

server_cam, addr = server.accept()
server_mot, addr = server.accept()
print('New Client connection')

flag_exit = False

# A thread that processes data received from the PC keyboard
def remote_mode() :
	while True:
		rl_byte = server_mot.recv(1)
		rl = struct.unpack('!B', rl_byte)
		if rl[0]==97:
			turnLeft(speedCurve)
		elif rl[0]==115:
			stopMotor()
		elif rl[0]==100:
			turnRight(speedCurve)
		elif rl[0]==119:
			goForward(speedFwd)
		elif rl[0]==120:
			goBackward(speedFwd)
		if flag_exit: break

motThread = threading.Thread(target=remote_mode)
motThread.start()

try:
	while True:
		cmd_byte = server_cam.recv(1)
		cmd = struct.unpack('!B', cmd_byte)
		if cmd[0]==12 :		

			# capture camera data
			ret,frame=cap.read()

			# Serialize frame
			data = pickle.dumps(frame)

			# send sensor + camera data
			data_size = struct.pack("!L", len(data)) 
			server_cam.sendall(data_size + data)

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
server_cam.close()
server_mot.close()
server.close()

exitMotor()
GPIO.cleanup()
