# Output the image data received from Pi on the PC screen
# and transmit the motor operation data to PI.
# Set PC as the socket communication client

# 01 Receive sensor value and video data
# 02 Convert video data and output video to PC screen
# 03 Command the Pi to move based on data
# 04 Create folders and save photos in each folder based on sensor values
# 05 Save csv file for labeling
# 06 It ends when the total number of photos is reached

import socket
import struct
import numpy as np
import cv2
import pickle
import time
import os
import csv

HOST_RPI = 'Raspberry Pi IP Address'
# User-selectable port number 1024~65535
PORT = 3232

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_mot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_cam.connect((HOST_RPI, PORT))
client_mot.connect((HOST_RPI, PORT))

t_now = time.time()
t_prev = time.time()
cnt_frame = 0
cnt_frame_total = 0

# Total number of saved photos
FRAME_TOTAL = 8000

# Set folder name in date and time format
# data.20230830_123456am
dirname = time.localtime(time.time())
dirname = time.strftime('%Y%m%d_%I%M%S%p',dirname)
dirname = "data.%s" %(dirname)

# Create parent and subfolders
os.mkdir(dirname)
os.mkdir(os.path.join(dirname, "left"))
os.mkdir(os.path.join(dirname, "right"))
os.mkdir(os.path.join(dirname, "forward"))

# Create csv a file
f_csv = open(os.path.join(dirname, "0_road_labels.csv"),'w', newline='')
wr = csv.writer(f_csv)
wr.writerow(["file","label"]) # line1 file, label

# Initializing a list with the name of the folder where video image data will be saved
names = ['forward', 'right', 'left', 'forward']

while True:

	# PI(server), send video and sensor values.
	cmd = 32
	cmd_byte = struct.pack('!B', cmd)
	client_cam.sendall(cmd_byte)

	# Receive sensor value
	rl_byte = client_cam.recv(1)
	rl = struct.unpack('!B', rl_byte)
	right, left = (rl[0] & 2)>>1, rl[0] & 1

	# Receive video data
	data_len_bytes = client_cam.recv(4)
	data_len = struct.unpack('!L', data_len_bytes)
	frame_data = client_cam.recv(data_len[0], socket.MSG_WAITALL)

	# Extract frame
	frame = pickle.loads(frame_data)

	# Output video to PC screen
	np_data = np.frombuffer(frame, dtype='uint8')
	frame = cv2.imdecode(np_data,1)
	frame2 = cv2.resize(frame, (320, 240))
	cv2.imshow('frame', frame2)

	# Save each folder to a folder according to the infrared sensor values.
	if not right or not left :
		road_file = time.localtime(time.time())
		road_file = time.strftime('%Y%m%d_%I%M%S%p', road_file)
		road_file = "%s.png" %(road_file)
		cv2.imwrite(
			os.path.join(os.path.join(dirname, names[rl[0]]), road_file),
			frame)
		wr.writerow([os.path.join(names[rl[0]], road_file),rl[0]])

	# PI(server),  move the car
	cmd = int(rl[0])
	cmd = struct.pack('!B', cmd)
	client_mot.sendall(cmd)

	key = cv2.waitKey(1)
	if key == 27:
		break

	if not right or not left :
		cnt_frame_total += 1
		if cnt_frame_total >= FRAME_TOTAL :
			break

	# Measuring frames per second
	cnt_frame += 1
	t_now = time.time()
	if t_now - t_prev >= 1.0 :
		t_prev = t_now
		print("frame count : %f" %cnt_frame, \
			"total frame : %d" %cnt_frame_total)
		cnt_frame = 0

client_cam.close()
client_mot.close()
f_csv.close()
