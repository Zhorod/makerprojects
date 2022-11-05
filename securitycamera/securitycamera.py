# python code for a motion detector and camera project
# 15th October 2022

import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from time import sleep

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessagefrom email.message import EmailMessage

ledPin = 12 # define ledPin
sensorPin = 11 # define sensorPin

#camera = PiCamera()
#sleep(2)
print('Initialised camera')

def setup():
    GPIO.setmode(GPIO.BOARD) # use PHYSICAL GPIO Numbering
    GPIO.setup(ledPin, GPIO.OUT) # set ledPin to OUTPUT mode
    GPIO.setup(sensorPin, GPIO.IN) # set sensorPin to INPUT mode

def loop():
    while True:
        if True:
        #if GPIO.input(sensorPin)==GPIO.HIGH:
            # we have detected some movement
            # turn on the LED and take a picture
            #GPIO.output(ledPin,GPIO.HIGH) # turn on led
            #now = time.localtime(time.time())
            now = "0000"
            filename = '/home/pi/Desktop/Images/image '+time.strftime("%c", now)+'.jpg'
            camera.capture(filename)

            # Create the container email message.
            msg = EmailMessage()
            msg['Subject'] = 'Security camera activated'
            # me == the sender's email address
            # family = the list of all recipients' email addresses
            msg['From'] = "input your email address"
            msg['To'] = "input your email address"
            msg.preamble = 'A Raspberry Pi security camera maker project image email.\n'

            # Open the file in binary mode.  You can also omit the subtype
            # if you want MIMEImage to guess it.
            fp = open(filename, 'rb')
            img_data = fp.read()
            fp.close()
            msg.add_attachment(img_data, maintype='image',subtype='png')

            # Send the email via our own SMTP server.
            with smtplib.SMTP('localhost') as s:
                s.send_message(msg)
            s.close
            print ('captured and sent image')
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