import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
import math
import datetime
import sys

from datetime import date
from datetime import datetime

adc=Adafruit_ADS1x15.ADS1115()

#set parameters

#gain for adc - default to 1
GAIN=1

#set variables

moisture_1_max = 19500 # calibrate from sensor
moisture_2_max = 19500
moisture_3_max = 19500
moisture_4_max = 19500

moisture_1_min = 9500 # calibrate from sensor
moisture_2_min = 9500
moisture_3_min = 9500
moisture_4_min = 9500

moisture_1_range = 10000 # calibrate from sensor
moisture_2_range = 10000
moisture_3_range = 10000
moisture_4_range = 10000

moisture_1_reading = 0 # globals to store the raw moisture readings
moisture_2_reading = 0
moisture_3_reading = 0
moisture_4_reading = 0

moisture_1_percent = 0 # globals to store the moisture readings as percentages
moisture_2_percent = 0
moisture_3_percent = 0
moisture_4_percent = 0

read_interval_time = 5 #seconds - this is time delay between sensor readings - default to 3600 (60 mins)
    
def write_moistures_stdout():
    
    # print the time and moisture data to standard out
    # if running as a service redirect to a log file in /var/log/water.log
    
    # create a datetime object containing current date and time
    now = datetime.now()

    # create a strong from the datetime object with the format dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    # print the date time string and mositure values
    print(dt_string+" %i %i %i %i" % (moisture_1_percent, moisture_2_percent, moisture_3_percent, moisture_4_percent))
    
    # flush the buffer
    sys.stdout.flush()

def read_moisture_1():
    global moisture_1
    global moisture_1_percent
    global moisture_1_reading
    
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(0, gain=GAIN)
    moisture_1_reading = max(values)
    moisture_1_percent = (int)((1.0-(float)((moisture_1_reading-moisture_1_min) / (moisture_1_range)))*100.0)
    
def read_moisture_2():
    global moisture_2
    global moisture_2_percent
    global moisture_2_reading
    
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(1, gain=GAIN)
    moisture_2_reading = max(values)
    moisture_2_percent = (int)((1.0-(float)((moisture_2_reading-moisture_2_min) / (moisture_2_range)))*100.0)

def read_moisture_3():
    global moisture_3
    global moisture_3_percent
    global moisture_3_reading
    
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(2, gain=GAIN)
    moisture_3_reading = max(values)
    moisture_3_percent = (int)((1.0-(float)((moisture_3_reading-moisture_3_min) / (moisture_3_range)))*100.0)

def read_moisture_4():
    global moisture_4
    global moisture_4_percent
    global moisture_4_reading
    
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(3, gain=GAIN)
    moisture_4_reading = max(values)
    moisture_4_percent = (int)((1.0-(float)((moisture_4_reading-moisture_4_min) / (moisture_4_range)))*100.0)

def loop():
    
    while True:
        
        # Read the mositure values
        read_moisture_1()
        #read_moisture_2()
        #read_moisture_3()
        read_moisture_4()
        
        # Print the moisture values to stdout 
        write_moistures_stdout()
        
        # Wait for a period of time
        time.sleep(read_interval_time)

if __name__ == '__main__':
    
    print("starting")

    try:
        loop()
    except KeyboardInterrupt:
        print("interupt received")
    finally:
        print("cleaned up - exiting")
