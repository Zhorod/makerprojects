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

start_watering = 70 # start watering when the moisture percentage is less than this percentage
stop_watering = 80 # stop watering when the moisture percentage is more than this percentage

pump_1_time = 35.0 # seconds - default 5.0
pump_2_time = 35.0 # seconds - default 5.0
pump_3_time = 35.0 # seconds - defailt 5.0
pump_4_time = 35.0 # seconds - default 5.0

pump_1_error = False
pump_2_error = False
pump_3_error = False
pump_4_error = False

read_interval_time = 3600 #seconds - this is time delay between sensor readings - default to 3600 (60 mins)
water_interval_time = 600 #seconds - this is the delay between pumps to allow water to spread to sensor - default 600 (10 mins)

max_water_cycles = 5 # the maximum number of water cycles before an error occurs - once triggered on a specific pump, pump wont water

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
    write_log_message("setup complete")
    
def water_1():
    
    # declare the global so we can change it if needed
    global pump_1_error
    
    # read the moisture level and store a local so we can test change after watering
    read_moisture_1()
    local_moisture_level_start = moisture_1_percent
    write_log_message("watering 1: start moisture: %i" % (moisture_1_percent))
    
    # run the pump for pump_1_seconds seconds
    run_pump_1(pump_1_time)
    
    # wait for water_interval_time to let the water spread before checking it has worked
    time.sleep(water_interval_time)
    
    # read the moisture level again and store the new value in a local variable
    read_moisture_1()
    local_moisture_level_end = moisture_1_percent
    write_log_message("watering 1: stop moisture: %i" % (moisture_1_percent))
    
    # check that the wat moisture percent has increased sufficiently or set an error flag
    if (local_moisture_level_start / local_moisture_level_end) > 0.95:
        
        # the water moisture did not seem to change
        # try destroying and redefining the GPIO
        destroy()
        setup()
        
        # try watering again
        # read the moisture level and store a local so we can test change after watering
        read_moisture_1()
        local_moisture_level_start = moisture_1_percent
        write_log_message("watering 1: start moisture: %i" % (moisture_1_percent))
        
        # run the pump for pump_1_time seconds
        run_pump_1(pump_1_time)
        
        # wait for water_interval_time to let the water spread before checking it has worked
        time.sleep(water_interval_time)
        
        # read the moisture level again and store the new value in a local variable
        read_moisture_1()
        local_moisture_level_end = moisture_1_percent
        write_log_message("watering 1: stop moisture: %i" % (moisture_1_percent))
        
        # check that the water moisture percent has increased
        # if it hasnt, set an error flag to avoid risk of flooding
        if (local_moisture_level_start / local_moisture_level_end) > 0.95 :
            pump_1_error = True
            write_log_message("error on pump 1")

def water_2():
    global pump_2_error
    number_water_cycles = 0
    
    write_log_message("watering 2: start moisture: %i" % (moisture_1_percent))
    while moisture_2_percent < stop_watering and pump_2_error == False:
        run_pump_2(pump_2_time)
        number_water_cycles += 1
        time.sleep(water_interval_time)
        read_moisture_2()
        write_log_message("watering 2: test  moisture: %i" % (moisture_2_percent))
        if moisture_2_percent < stop_watering and number_water_cycles == max_water_cycles:
            pump_2_error = True
            write_log_message("watering 2: error - too many water cycles")
    write_log_message("watering 2: stop  moisture: %i" % (moisture_2_percent))
        
def water_3():
    global pump_3_error
    number_water_cycles = 0
    
    write_log_message("watering 3: start moisture: %i" % (moisture_3_percent))
    while moisture_3_percent < stop_watering and pump_3_error == False:
        write_log_message("watering 3: active - moisture: %i" % (moisture_3_percent))
        run_pump_3(pump_3_time)
        number_water_cycles += 1
        time.sleep(water_interval_time)
        read_moisture_3()
        write_log_message("watering 3: test  moisture: %i" % (moisture_3_percent))
        if moisture_3_percent < stop_watering and number_water_cycles == max_water_cycles:
            pump_3_error = True
            write_log_message("Watering 3: error - too many water cycles")
    write_log_message("watering 3: stop  moisture: %i" % (moisture_3_percent))
        
def water_4():
    # declare the global so we can change it if needed
    global pump_4_error
    
    # read the moisture level and store a local so we can test change after watering
    read_moisture_4()
    local_moisture_level_start = moisture_4_percent
    write_log_message("watering 4: start moisture: %i" % (moisture_4_percent))
    
    # run the pump for pump_4_seconds seconds
    run_pump_4(pump_4_time)
    
    # wait for water_interval_time to let the water spread before checking it has worked
    time.sleep(water_interval_time)
    
    # read the moisture level again and store the new value in a local variable
    read_moisture_4()
    local_moisture_level_end = moisture_4_percent
    write_log_message("watering 4: stop moisture: %i" % (moisture_4_percent))
    
    # check that the water moisture percent has increased sufficiently or set an error flag
    if (local_moisture_level_start / local_moisture_level_end) > 0.95 :
        
        # the water moisture did not seem to change
        # try destroying and redefining the GPIO
        destroy()
        setup()
        
        # try watering again
        # read the moisture level and store a local so we can test change after watering
        read_moisture_4()
        local_moisture_level_start = moisture_4_percent
        write_log_message("watering 4: start moisture: %i" % (moisture_4_percent))
        
        # run the pump for pump_4_time seconds
        run_pump_4(pump_4_time)
        
        # wait for water_interval_time to let the water spread before checking it has worked
        time.sleep(water_interval_time)
        
        # read the moisture level again and store the new value in a local variable
        read_moisture_4()
        local_moisture_level_end = moisture_4_percent
        write_log_message("watering 4: stop moisture: %i" % (moisture_4_percent))
        
        # check that the water moisture percent has increased
        # if it hasnt, set an error flag to avoid risk of flooding
        if (local_moisture_level_start / local_moisture_level_end) > 0.95 :
            pump_4_error = True
            write_log_message("error on pump 4")

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
    
    # try to open the log file
    try:
        moisture_data_file = open(moisture_data_file_name,"a")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        write_log_message("error opening the file: %s" % (log_file))
        return false
    
    # create a datetime object containing current date and time
    now = datetime.now()

    # create a strong from the datetime object with the format dd/mm/YY H:M:S
    date_string = now.strftime("%d/%m/%Y")
    time_string = now.strftime("%H:%M:%S")
    
    # write date, time and moistures to data file
    moisture_data_file.write("%s %s,%i,%i,%i,%i\n" % (date_string, time_string, moisture_1_percent, moisture_2_percent, moisture_3_percent, moisture_4_percent))
    
    moisture_data_file.close()
    
def write_stdout():
    
    # print the time and moisture data to standard out
    # if running as a service redirect to a log file in /var/log/water.log
    
    # create a datetime object containing current date and time
    now = datetime.now()

    # create a strong from the datetime object with the format dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    # print the date time string and mositure values
    print(dt_string+" %i %i %i %i" % (moisture_1_percent, moisture_2_percent, moisture_3_percent, moisture_4_percent))
    
    sys.stdout.flush()
    
def write_log_message(message):
    
    # try to open the log file
    try:
        log_file = open(moisture_log_file_name,"a")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        print("error opening the file: %s" % (log_file))
        return false
    
    # create a datetime object containing current date and time
    now = datetime.now()

    # create a strong from the datetime object with the format dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    # write date, time and message to log file and stdout
    log_file.write("%s %s\n" % (dt_string, message))
    print("%s %s" %(dt_string, message))
    
    log_file.close()

def read_moisture_1():
    
    # declare global variables locally to allow change
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
        
        # read the mositure values
        read_moisture_1()
        #read_moisture_2()
        #read_moisture_3()
        read_moisture_4()
        
        # print the moisture values to the moisture data file
        write_data_file()
        
        # check each channel and water if current moisture is less that the start_watering
        # threshold for that channel and there is no error flag on pump
        if moisture_1_percent < start_watering and pump_1_error == False:
            water_1()
            
        #if moisture_2_percent < start_watering and pump_2_error = False:
        #    water_2()
        
        #if moisture_3_percent < start_watering and pump_3_error = Fales:
        #    water_3()
        
        if moisture_4_percent < start_watering and pump_4_error == False:
            water_4()
        
        # wait for read_internal_time seconds to avoid high processor load
        time.sleep(read_interval_time)

def destroy():
    write_log_message("closing connections")
    GPIO.output(PUMP_PIN_1, GPIO.HIGH)
    GPIO.output(PUMP_PIN_2, GPIO.HIGH)
    GPIO.output(PUMP_PIN_3, GPIO.HIGH)
    GPIO.output(PUMP_PIN_4, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    
    # run set up
    setup()
    
    write_log_message("starting")

    try:
        loop()
    except KeyboardInterrupt:
        write_log_message("interupt received")
    finally:
        destroy()
        write_log_message("cleaned up - exiting")
