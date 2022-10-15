# python code for a motion detector and camera project
# 15th October 2022

import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from time import sleep

ledPin = 12 # define ledPin
sensorPin = 11 # define sensorPin

camera = PiCamera()
sleep(2)
print('Initialised camera')

def setup():
    GPIO.setmode(GPIO.BOARD) # use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT) # set ledPin to OUTPUT mode
    GPIO.setup(sensorPin, GPIO.IN) # set sensorPin to INPUT mode

def loop():
    while True:
        if GPIO.input(sensorPin)==GPIO.HIGH:
            # we have detected some movement
            # turn on the LED and take a picture
            GPIO.output(ledPin,GPIO.HIGH) # turn on led
            now = time.localtime(time.time())
            camera.capture('/home/pi/Desktop/Images/image '+time.strftime("%c", now)+'.jpg')
            
            print ('captured images')
        else:
            GPIO.output(ledPin,GPIO.LOW) # turn off led

def destroy():
	GPIO.cleanup() # Release GPIO resource

if __name__ == '__main__': # Program entrance
	print ('Program is starting...')
	setup()
	try:
		loop()
	except KeyboardInterrupt: # Press ctrl-c to end the program.
		destroy()