
import RPi.GPIO as GPIO
import time
import Adafruit_ADS1x15
import math
import datetime
import sys




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

moisture_1_dry = 14000
moisture_2_dry = 14000
moisture_3_dry = 14000
moisture_4_dry = 14000

moisture_1_moist = 12000
moisture_2_moist = 12000
moisture_3_moist = 12000
moisture_4_moist = 12000

moisture_1 = 0
moisture_2 = 0
moisture_3 = 0
moisture_4 = 0

pump_1_time = 1.0 #seconds
pump_2_time = 1.0 #seconds
pump_3_time = 1.0 #seconds
pump_4_time = 1.0 #seconds

read_interval_time = 300 #seconds - this is time delay between sensor readings - default to 600
water_interval_time = 30 #seconds - this is the delay between pumps to allow water to spread to sensor - default 30


moisture_data_file_name = "/home/mirror/GrowFiles/grow_moisture_data.txt"
moisture_log_file_name = "/home/mirror/GrowFiles/grow_log_data.txt"


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
    
def water_1():
    while moisture_1 > moisture_1_moist:
        write_log_data("watering 1: moisture: %i" % (moisture_1))
        run_pump_1(pump_1_time)
        time.sleep(water_interval_time)
        read_moisture_1()
    write_log_data("watering 1 ended: moisture: %i" % (moisture_1))

def water_2():
    while moisture_2 > moisture_2_moist:
        write_log_data("watering 2: moisture: %i" % (moisture_2))
        run_pump_2(pump_2_time)
        time.sleep(water_interval_time)
        read_moisture_2()
    write_log_data("watering 2 ended: moisture: %i" % (moisture_2))
        
def water_3():
    while moisture_3 > moisture_3_moist:
        write_log_data("watering 3: moisture: %i" % (moisture_3))
        run_pump_3(pump_3_time)
        time.sleep(water_interval_time)
        read_moisture_3()
    write_log_data("watering 3 ended: moisture: %i" % (moisture_3))
        
def water_4():
    while moisture_4 > moisture_4_moist:
        write_log_data("watering 4: moisture: %i" % (moisture_4))
        run_pump_4(pump_4_time)
        time.sleep(water_interval_time)
        read_moisture_4()
    write_log_data("watering 4 ended: moisture: %i" % (moisture_4))

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
    
def write_data_file():
    result = open(moisture_data_file_name,"a")
    
    #write date and time
    e = datetime.datetime.now()
    result.write("%s,%s,%s,%s,%s," % (e.day, e.month, e.year, e.hour, e.minute))
    
    #write moistures
    result.write("%i,%i,%i,%i" % (moisture_1, moisture_2, moisture_3, moisture_4))
    
    #write newline
    result.write("\n")
    
    result.close()
    
def write_log_data(message):
    
    print(message)
    
    result = open(moisture_log_file_name,"a")
    
    #write date and time
    e = datetime.datetime.now()
    result.write("%s %s %s %s %s" % (e.day, e.month, e.year, e.hour, e.minute))
    
    #write space
    result.write(" " )
    
    #write log
    result.write(message)
    
    #write newline
    result.write("\n")
    
    result.close()

def read_moisture_1():
    global moisture_1
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(0, gain=GAIN)
    moisture_1 = max(values)
    
def read_moisture_2():
    global moisture_2
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(1, gain=GAIN)
    moisture_2 = max(values)

def read_moisture_3():
    global moisture_3
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(2, gain=GAIN)
    moisture_3 = max(values)

def read_moisture_4():
    global moisture_4
    values = [0]*100
    for i in range(100):
        values[i] = adc.read_adc(3, gain=GAIN)
    moisture_4= max(values)

def loop():
    
    while True:
        read_moisture_1()
        print("moisture sensor 1: ",moisture_1)
        if(moisture_1 > moisture_1_dry):
            water_1()
        read_moisture_2()
        print("moisture sensor 2: ",moisture_2)
        if(moisture_2 > moisture_2_dry):
            water_2()
        read_moisture_3()
        print("moisture sensor 3: ",moisture_3)
        if(moisture_3 > moisture_3_dry):
            water_3()
        read_moisture_4()
        print("moisture sensor 4: ",moisture_4)
        if(moisture_4 > moisture_4_dry):
            water_4()
        write_data_file()
        sys.stdout.flush()
        time.sleep(read_interval_time)

def destroy():
    print("closing connections")
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()

    try:
        loop()
    except KeyboardInterrupt:
        print("interupt received")
    finally:
        destroy()
