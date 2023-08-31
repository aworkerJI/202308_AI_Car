## Step04_Collect_data
### Stores data to be used for CNN artificial neural network learning.

### PI and PC communicate with TCP socket
### PC receives real-time video and infrared sensor input from PI
### Transfer data from PC to PI for motor control

#### Set PI as the socket communication server
#### 01 Transmission to PC of infrared sensor values and camera data
#### 02 Running a thread with data received from a PC
####
#### Set PC as the socket communication client
#### Output the image data received from Pi on the PC screen
#### and transmit the motor operation data to PI.
#### 01 Receive sensor value and video data
#### 02 Convert video data and output video to PC screen
#### 03 Command the Pi to move based on data
#### 04 Create folders and save photos in each folder based on sensor values
#### 05 Save csv file for labeling

## Photos related to the project
### 
<img src="https://github.com/aworkerJI/202308_AI_Car/assets/59903316/0127512d-2f18-4bf1-8488-34758a773eef.gif" width="550" height="350"/>


###
<img src="https://github.com/aworkerJI/202308_AI_Car/assets/59903316/2a4b693f-b52f-4397-a848-78ea1f22651a.png" width="550" height="350"/>


###
<img src="https://github.com/aworkerJI/202308_AI_Car/assets/59903316/30e050bb-45b5-4428-8bd0-ca6373f19e9f.png" width="550" height="350"/>


###
<img src="https://github.com/aworkerJI/202308_AI_Car/assets/59903316/4fc663f3-b14e-428f-9d7b-a521b98ad794.png" width="550" height="350"/>




