
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
import math

adc=Adafruit_ADS1x15.ADS1115()

GAIN=1

DRY = 18000

# pins for water pumps
PUMP_PIN_1=7
PUMP_PIN_2=11
PUMP_PIN_3=13
PUMP_PIN_4=15

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PUMP_PIN_1, GPIO.OUT)
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.setup(PUMP_PIN_2, GPIO.OUT)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.setup(PUMP_PIN_3, GPIO.OUT)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
#    GPIO.setup(PUMP_PIN_4, GPIO.OUT)
#    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    time.sleep(0.5)
    
    
def run_pump_1(num_seconds):
    GPIO.output(PUMP_PIN_1, GPIO.LOW)
    time.sleep(num_seconds)
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)

def run_pump_2(num_seconds):
    GPIO.output(PUMP_PIN_2, GPIO.LOW)
    time.sleep(num_seconds)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)

def run_pump_3(num_seconds):
    GPIO.output(PUMP_PIN_3, GPIO.LOW)
    time.sleep(num_seconds)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
    
def run_pump_4(num_seconds):
    GPIO.output(PUMP_PIN_4, GPIO.LOW)
    time.sleep(num_seconds)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)

def read_moisture_1():
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(0, gain=GAIN)
    return(max(values))
    
def read_moisture_2():
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(1, gain=GAIN)
    return(max(values))

def read_moisture_3():
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(2, gain=GAIN)
    return(max(values))

def read_moisture_4():
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(3, gain=GAIN)
    return(max(values))

def loop():
    while True:
        time.sleep(1)
        moisture_1 = read_moisture_1()
        print("moisture sensor 1: ",moisture_1)
        if(moisture_1 > DRY):
            print("moisture sensor 1 showing dry: ",moisture_1)
            print("watering")
#            run_pump_1(0.5)
            time.sleep(0.1)
        moisture_2 = read_moisture_2()
        print("moisture sensor 2: ",moisture_2)
        if(moisture_2 > DRY):
            print("moisture sensor 2 showing dry: ",moisture_2)
            print("watering")
#            run_pump_2(0.5)
            time.sleep(0.1)
        moisture_3 = read_moisture_3()
        print("moisture sensor 3: ",moisture_3)
        if(moisture_3 > DRY):
            print("moisture sensor 3 showing dry: ",moisture_3)
            print("watering")
#            run_pump_3(0.5)
            time.sleep(0.1)
#        moisture_4 = read_moisture_4()
#        print("moisture sensor 4: ",moisture_4)
#        if(moisture_4 > DRY):
#            print("moisture sensor 4 showing dry: ",moisture_4)
#            print("watering")
#            run_pump_4(0.5)
#            time.sleep(0.1)


def destroy():
    print("closing connections")
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
#    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("interupt received")
    destroy()
