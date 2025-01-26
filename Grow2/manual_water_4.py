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

# pins for water pumps
PUMP_PIN_1=7
PUMP_PIN_2=11
PUMP_PIN_3=13
PUMP_PIN_4=15

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

pump_1_time = 5.0 # seconds - default 5.0
pump_2_time = 5.0 # seconds - default 5.0
pump_3_time = 5.0 # seconds - defailt 5.0
pump_4_time = 5.0 # seconds - default 5.0

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PUMP_PIN_1, GPIO.OUT)
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.setup(PUMP_PIN_2, GPIO.OUT)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.setup(PUMP_PIN_3, GPIO.OUT)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
    GPIO.setup(PUMP_PIN_4, GPIO.OUT)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    time.sleep(0.5)
    print("setup complete")
    sys.stdout.flush()
        
def water_4():
    read_moisture_4()
    print("Watering 4: start moisture: %i" % (moisture_4_percent))
    run_pump_4(pump_4_time)
    time.sleep(5)
    read_moisture_4()
    print("Watering 4: stop  moisture: %i" % (moisture_4_percent))
    sys.stdout.flush()
    
def run_pump_4(num_seconds):
    GPIO.output(PUMP_PIN_4, GPIO.LOW)
    time.sleep(num_seconds)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    
def read_moisture_4():
    global moisture_4
    global moisture_4_percent
    global moisture_4_reading
    
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(3, gain=GAIN)
    moisture_4_reading = max(values)
    moisture_4_percent = (int)((1.0-(float)((moisture_4_reading-moisture_4_min) / (moisture_4_range)))*100.0)
            
def destroy():
    print("closing connections")
    sys.stdout.flush()
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    
    # run set up
    setup()
    
    print("starting")
    sys.stdout.flush()

    try:
        water_4()
    except KeyboardInterrupt:
        print("interupt received")
        sys.stdout.flush()
    finally:
        destroy()
        print("cleaned up - exiting")
        sys.stdout.flush()
