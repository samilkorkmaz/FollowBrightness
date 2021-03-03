#Move marker towards brightness circle center with stepper motors
#Brightness detection from: https://www.pyimagesearch.com/2014/09/29/finding-brightest-spot-image-using-python-opencv/
from videoUtils import CaptureVideo
from control import generateCommands, Kp
from firstOrderSystem import calcState
#from motor import moveMotor, GPIOCleanup, calcDelay_s
import threading
import time
import numpy as np
import cv2

captureVideo = CaptureVideo()

width  = captureVideo.cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = captureVideo.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
centerX = width/2
centerY = height/2
markerX = centerX
markerY = centerY

print("width: ", width, ", height: ", height)
radius = 41 #must be an odd number, or else GaussianBlur will fail
circleColor = (0, 0, 255) #BGR
circleThickness = 15

tGetFrame = threading.Thread(target = captureVideo.get_frame, args = [])
tGetFrame.start()

time.sleep(2) #wait for camera frame to stabilize (initial frame is black)
try:
    while True:    
        image = captureVideo.frame.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # apply a Gaussian blur to the image then find the brightest region
        gray = cv2.GaussianBlur(gray, (radius, radius), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        #Move marker towards brightness circle center. The marker is modelled as a first order system with PI control
        [forceX, forceY, errorStr] = generateCommands(maxLoc, [markerX, markerY], captureVideo.timeStep_s)
        
        [markerX, markerY] = calcState([forceX, forceY], [markerX, markerY], captureVideo.timeStep_s)
        '''minForceX = 0
        maxForceX = Kp*width/2
        minForceY = 0
        maxForceY = Kp*height/2
        delayX_s = calcDelay_s(minForceX, maxForceX, forceX)
        delayY_s = calcDelay_s(minForceY, maxForceY, forceY)
        moveMotorXOneStep(delayX_s, forceX > 0)
        moveMotorYOneStep(delayY_s, forceY > 0)
        time.sleep(.5)'''
        
        image = captureVideo.frame.copy()
        image = cv2.putText(image, errorStr, (0,100), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA) 
        cv2.drawMarker(image, ((int)(markerX), (int)(markerY)), (255,0,0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=4, line_type=cv2.LINE_AA)
        cv2.circle(image, maxLoc, radius, circleColor, circleThickness)
        # display the results of our newly improved method
        cv2.imshow("Robust", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print('CTRL+C pressed.')        
finally:
    captureVideo.run = False #stop video capture thread
    #GPIOCleanup()
    print("Main thread ended.")