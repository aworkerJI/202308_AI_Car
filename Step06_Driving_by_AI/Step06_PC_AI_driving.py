# Motor control is based on prediction of real-time video images
# through CNN neural network.

# 01 Paste the video images received from the camera server
#    alternately into the message queue and continue receiving the next video.
# 02 Pull the video image from the allocated message queue, perform prediction through CNN neural network,
# 03 Deliver the result to the Raspberry Pi's motor control thread.
import socket
import struct
import numpy as np
import cv2
import pickle
import time
from tensorflow.keras.models import load_model
import tensorflow as tf
import threading
import queue

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

model = load_model('model.h5')

names = ['forward', 'right', 'left', 'forward']

NUM_MESSAGES = 10

# Create two message queues
mq = [queue.Queue(NUM_MESSAGES), queue.Queue(NUM_MESSAGES)]

flag_exit = False


# 01 Pull the video image from the allocated message queue, perform prediction through CNN neural network,
# 02 Deliver the result to the Raspberry Pi's motor control thread.
def cnn_main(args) :
	while True:
		frame = mq[args].get()
		image = frame
		image = image/255

		image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)

		# Add dimension to match with input mode
		image_tensor = tf.expand_dims(image_tensor, 0)

		y_predict = model.predict(image_tensor)
		y_predict = np.argmax(y_predict,axis=1)

		# send y_predict
		cmd = y_predict[0].item()
		if cmd == 0:
			print('Forward\n')
		elif cmd == 1:
			print('turnRight\n')
		elif cmd == 2:
			print('turnLeft\n')
		cmd = struct.pack('B', cmd)
		client_mot.sendall(cmd)

		if flag_exit: break

cnnThread_0 = threading.Thread(target=cnn_main, args=(0,))
cnnThread_0.start()
cnnThread_1 = threading.Thread(target=cnn_main, args=(1,))
cnnThread_1.start()

fn = 0


# Paste the video images received from the camera server
# alternately into the message queue and continue receiving the next video.
try:
	while True:
		# PI(server), send video and sensor values
		cmd = 12
		cmd_byte = struct.pack('!B', cmd)
		client_cam.sendall(cmd_byte)

		# Receive sensor value
		rl_byte = client_cam.recv(1)

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

		# Insert video image into message queue
		mq[fn%2].put(frame)
		fn += 1

		key = cv2.waitKey(1)
		if key == 27:
			break

		''' 
		# Measuring frames per second
		cnt_frame += 1
		t_now = time.time()
		if t_now - t_prev >= 1.0 :
			t_prev = t_now
			print("frame count : %f" %cnt_frame)
			cnt_frame = 0
		'''
except:
	pass

flag_exit = True
cnnThread_0.join()
cnnThread_1.join()
client_cam.close()
client_mot.close()