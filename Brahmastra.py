print('''
#Created By: nishantKr18
##################################
#     #  #            #   ##      
# #   #  #            #  #  #     
#  #  #  # ##  # ##   #   ##      
#   # #  ##    ##     #  #  #     
#    ##  # ##  #      #   ##      
################################## 
''')

import cv2
import numpy as np
from segmenter import detectHand , reset
from keras.models import load_model
import vlc
import serial
from time import sleep
from pynput.mouse import Button, Controller
m = Controller()

player = vlc.MediaPlayer('AVENGERS.mp4')

def moveBot(ch, speedMotor = '80'):
	if(ch == 'AC'):ser.write(str.encode('1 0 0 0 0 0 0 '+'65'+'\n'));
	elif(ch == 'C'):ser.write(str.encode('0 1 0 0 0 0 0 '+'65'+'\n'));
	elif(ch == 'F'):ser.write(str.encode('0 0 1 0 0 0 0 '+speedMotor+'\n'));
	elif(ch == 'B'):ser.write(str.encode('0 0 0 1 0 0 0 '+speedMotor+'\n'));
	elif(ch == 'S1u'):ser.write(str.encode('0 0 0 0 1 0 0 '+speedMotor+'\n'));
	elif(ch == 'S1d'):ser.write(str.encode('0 0 0 0 -1 0 0 '+speedMotor+'\n'));
	elif(ch == 'S2d'):ser.write(str.encode('0 0 0 0 0 1 0 '+speedMotor+'\n'));
	elif(ch == 'S2u'):ser.write(str.encode('0 0 0 0 0 -1 0 '+speedMotor+'\n'));
	elif(ch == 'S3u'):ser.write(str.encode('0 0 0 0 0 0 1 '+speedMotor+'\n'));
	elif(ch == 'S3d'):ser.write(str.encode('0 0 0 0 0 0 -1 '+speedMotor+'\n'));
	else: ser.write(str.encode('0 0 0 0 0 0 0 0\n'));
	ser.readline()
	print(ch)


ser = serial.Serial("/dev/ttyACM0", 9600)
sleep(2)
print("connection Est");

cap = cv2.VideoCapture(0)

def stateHasChanged():
	a = '''
	------------------------------------------------------
	----------------STATE HAS CHANGED--------------------
	------------------------------------------------------
	'''
	print(a)

print("loading model")
model = load_model("MyModel.hand")
labelz = dict(enumerate(['fist', 'fistWH', 'A1', 'A2', 'A3', 'A6', 'A9', 'A12', 'A15', 'call', 'crock', 'four', 'LL', 'LR', 'ok', 'one', 'oneL', 'oneR', 'palm', 'pinky', 'three', 'tL', 'tR', 'VL', 'VR', 'VU']))
states = dict(enumerate(['one', 'VU', 'three', 'A15', 'crock', 'VL']))

label = None
feed = None
toggle = False
Px = 0
Py = 0
resizeVar = [250, 250]
moveVar = [250, 250]


controller = [ 375, 500, 125, 250] # x1<x2 y1<y2
newToggle = False

PrevLocation = [0,0]

state = 1 #Default state
counter = 0
arrayOfPrevious = [''] * 30

def movementOfMouse(factor, thres):
	global PrevLocation
	global Px
	global Py
	ans = [int((Px-PrevLocation[0])*factor), int((Py- PrevLocation[1])*factor)]
	if(abs(ans[0])<thres):ans[0]=0
	if(abs(ans[1])<thres):ans[1]=0
	return ans


while True:
	_F, frame = cap.read()
	thresholded, temp, rect = detectHand(frame, cap, show = False) # rect : x1, y1, x2, y2 hand is the binary image
	if thresholded is not None:
		thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
		cv2.circle(thresholded, (Px,Py), 10, (0, 255, 0), -1)
		cv2.line(thresholded,(controller[0],0),(controller[0],thresholded.shape[0]),(200, 0, 0), 2); 
		cv2.line(thresholded,(controller[1],0),(controller[1],thresholded.shape[0]),(200, 0, 0), 2); 
		cv2.line(thresholded,(0, controller[2]),(thresholded.shape[1], controller[2]),(200, 0, 0), 2); 
		cv2.line(thresholded,(0, controller[3]),(thresholded.shape[1], controller[3]),(200, 0, 0), 2);
		if temp is not None: 
			Px, Py = rect[0:2]
			Px+=int(rect[2]/2)
			cv2.imshow('temp', temp)
			temp = temp.reshape(-1, 100, 100, 1)
			if(toggle == True):
				class_prediction = model.predict_classes(temp, verbose = False)[0]
				percent = round(max(model.predict_proba(temp, verbose = False)[0])*100)
				if(percent>=98):label = labelz[class_prediction]
				else: label = None
				# print(label,' percent accu: ' ,percent, ' current State: ', state)
			else:
				label = None
		cv2.putText(thresholded,'current State: '+str(state),(25,25), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2,cv2.LINE_AA)
		if(label!=None): cv2.putText(thresholded,label+' '+str(percent)+'%',(25,75), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0),2,cv2.LINE_AA)
		cv2.imshow('thresholded',thresholded)

	if(newToggle):
		for i in range(len(states)):
			if(label == states[i]):
				stateHasChanged()
				state = i+1
		newToggle = False

	present = False
	for i in range(len(states)):
		if(label == states[i]):
			present = True
			break
	if (present):
		arrayOfPrevious[counter] = label
		if(counter == len(arrayOfPrevious)-1): itr = -1
		elif(counter == 0): itr = 1
		counter += itr

		if(states[state-1] != arrayOfPrevious[0]):
			newToggle = True
			for i in arrayOfPrevious:
				if(i != arrayOfPrevious[0]):
					newToggle = False
					break

	if(state == 1):
		cv2.namedWindow('feed', flags=cv2.WINDOW_NORMAL)
		if(label == 'palm'):
			pass
		else:
			feed = frame.copy()
			feed = cv2.flip(feed, 1)
			if(label == 'A6'):
				cv2.resizeWindow('feed', (resizeVar[0], resizeVar[1]) )
				if(resizeVar[0]<20): resizeVar[0]=20
				if(resizeVar[1]<20): resizeVar[1]=20
				resizeVar[0]+=movementOfMouse(3,0)[0]
				resizeVar[1]+=movementOfMouse(3,0)[1]


			elif(label == 'fistWH'): 
				cv2.moveWindow('feed', moveVar[0], moveVar[1])
				if(moveVar[0]<0): moveVar[0]=0
				if(moveVar[1]<0): moveVar[1]=0
				if(moveVar[0]>1650): moveVar[0]=1650
				if(moveVar[1]>700): moveVar[1]=700
				moveVar[0]+=movementOfMouse(3,0)[0]
				moveVar[1]+=movementOfMouse(3,0)[1]

			elif(label == 'A1'): 
				feed = cv2.GaussianBlur(feed,(95,95),0)
			elif(label == 'A2'):
				feed = cv2.cvtColor(feed, cv2.COLOR_BGR2GRAY) 
			elif(label == 'A3'):
				feed = np.copy(thresholded)
		if feed is not None: cv2.imshow('feed', feed)
	else: cv2.destroyWindow('feed')

	if(state == 2):
		if(label == 'fist'):
			if(Px<controller[0]):moveBot('AC')
			elif(Px>controller[1]):moveBot('C')
			elif(Py<controller[2]):moveBot('F')
			elif(Py>controller[3]):moveBot('B')
			else: moveBot('S')
		elif(label == 'fistWH'):
			if(Px<controller[0]):moveBot('S1u')
			elif(Px>controller[1]):moveBot('S1d')
			elif(Py<controller[2]):moveBot('S2u')
			elif(Py>controller[3]):moveBot('S2d')
			else: moveBot('S')
		elif(label == 'tR' or label == 'tL'):
			if(Px<controller[0]):moveBot('S3u')
			elif(Px>controller[1]):moveBot('S3d')
			else: moveBot('S')
		else:
			moveBot('S')

	if(state == 3):
		if(label == 'A12'):
			if(player.is_playing()): player.pause()
		elif(label == 'ok'):
			player.stop()
		elif(label == 'fist'):
			player.play()
		elif(label == 'A6'):
			val = int((thresholded.shape[1]-Py-200)/thresholded.shape[1]*200)
			print('Volume Set to : ', val)
			player.audio_set_volume(val)
		elif(label == 'LL'):
			player.set_fullscreen(True)
		elif(label == 'LR'):
			player.audio_set_mute(True)
		if(label != 'LL'):
			player.set_fullscreen(False)
		if(label != 'LR'):
			player.audio_set_mute(False)
	else: player.stop()

			
	if(state == 4):
		if(label == 'four'):
			print('GOOD AFTERNOON!!!!!!!!!!!---------------------------------------------------------------')
		elif(label == 'call'):
			print('YOU CAN ADD FUNCTIONALLITY FOR CALL HERE------------------------------------------------')
		elif(label == 'oneR'):
			print('YOU ARE POINTING TO RIGHT---------------------------------------------------------------')
		elif(label == 'oneL'):
			print('YOU ARE POINTING	TO LEFT----------------------------------------------------------------')
		elif(label == 'VR'):
			print('IIT BHU ROCKS---------------------------------------------------------------------------')
		elif(label == 'A9'):
			print('WONDER WHICH FINGER?????----------------------------------------------------------------')

	if(state == 5):
		if(label == 'fist'):
			ans = movementOfMouse(4, 5)
			m.move(ans[0], ans[1])

	if(state == 6):
		moveBot('S')
		break


	key = cv2.waitKey(1)
	if key == ord('q'):
		moveBot('S')
		break
	elif key == ord('a'):
		print('RESET')
		moveBot('S')
		reset()
	elif key == ord('s'):
		print('PREDICTION HAS STARTED')
		toggle = True
		moveBot('S')
	elif key == ord('p'):
		print('PREDICTION HAS BEEN PAUSED')
		toggle = False
		moveBot('S')

	PrevLocation = [Px, Py]
        
