# Output the image data received from Pi on the PC screen
# and transmit the motor operation data to PI.
# Set PC as the socket communication client
# 01 Receive video data
# 02 Convert video data and output video to PC screen
# 03 Command the Pi to move based on data


import socket
import struct
import numpy as np
import cv2
import pickle
import time
import threading
HOST_RPI = 'Raspberry Pi IP Address'
PORT = 3232

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_mot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_cam.connect((HOST_RPI, PORT))
client_mot.connect((HOST_RPI, PORT))

flag_exit = False


# w : go straight / a : turn left / s : stop / d : turn right / x: back up
def Key_input() :
	while True:
		cmd = input("contorl? : ")
		if cmd== 'a':
			cmd_byte=struct.pack('!B', 97)
			client_mot.sendall(cmd_byte)
			print('send a turnLeft')	
		elif cmd == 's':
			cmd_byte=struct.pack('!B',115)
			client_mot.sendall(cmd_byte)
			print('send s stopMotor')
		elif cmd == 'd':
			cmd_byte=struct.pack('!B',100)
			client_mot.sendall(cmd_byte)
			print('send d turnRight')
		elif cmd == 'w':
			cmd_byte=struct.pack('!B', 119)
			client_mot.sendall(cmd_byte)
			print('send w goForward')
		elif cmd == 'x':
			cmd_byte=struct.pack('!B', 120)
			client_mot.sendall(cmd_byte)
			print('send x goBackward')

		if flag_exit: break
		
KeyThread = threading.Thread(target=Key_input)
KeyThread.start()

try:
	while True:

		# PI(server), send video and sensor values.
		cmd = 12
		cmd_byte = struct.pack('!B', cmd)
		client_cam.sendall(cmd_byte)

		# Receive sensor value
		data_len_bytes = client_cam.recv(4)
		data_len = struct.unpack('!L', data_len_bytes)
		frame_data = client_cam.recv(data_len[0], socket.MSG_WAITALL)

		# Receive video data
		frame = pickle.loads(frame_data)

		# Extract frame
		np_data = np.frombuffer(frame, dtype='uint8')
		frame = cv2.imdecode(np_data,1)
		frame2 = cv2.resize(frame, (800, 600))
		cv2.imshow('frame', frame2)

		key = cv2.waitKey(1)

		if key == 27:
			break

except KeyboardInterrupt:
	pass
except	ConnectionResetError:
	pass
except BrokenPipiError:
	pass
except:
	pass
flag_exit = True
KeyThread.join()
client_cam.close()
client_mot.close()
