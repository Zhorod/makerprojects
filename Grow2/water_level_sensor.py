import math
import datetime
import time
import sys
import statistics

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
  
import RPi.GPIO as GPIO

MAX_DISTANCE = 220


class WaterLevelSensor:
  
  # define class variables - all instances share varaible
  
  def __init__(self, active, trig_pin, echo_pin, full_distance, empty_distance):
    
    # define instance variables
    
    self.trig_pin = trig_pin
    self.echo_pin = echo_pin
    self.full_distance = full_distance
    self.empty_distance = empty_distance
    self.max_distance = MAX_DISTANCE
    self.timeout = self.max_distance*60
    self.active = active
      
    GPIO.setup(self.trig_pin, GPIO.OUT) # set trigPin to output mode
    GPIO.setup(self.echo_pin, GPIO.IN) # set echoPin to input mode
  
  def pulse_in(self,level,timeOut): # function pulseIn: obtain pulse time of a pin
    t0 = time.time()
    while(GPIO.input(self.echo_pin) != level):
      if((time.time() - t0) > timeOut*0.000001):
        return 0;
    t0 = time.time()
    while(GPIO.input(self.echo_pin) == level):
      if((time.time() - t0) > timeOut*0.000001):
        return 0;
    pulseTime = (time.time() - t0)*1000000
    return pulseTime
  
  def get_water_level(self):
    if (self.active == True):
      water_level = 0.0
      
      GPIO.output(self.trig_pin,GPIO.HIGH) #make trigPin send 10us high level
      time.sleep(0.00001) #10us
      GPIO.output(self.trig_pin,GPIO.LOW)
      
      ping_time = self.pulse_in(GPIO.HIGH,self.timeout)
      distance = ping_time * 340.0 / 2.0 / 10000.0 # the sound speed is 340m/s, and calculate distance (cm)
      
      # temp print statement
      # print("The distance is %f - full is %f - empty is %f"%(distance, self.full_distance, self.empty_distance))
       
      if distance < self.full_distance:
        # the distance is less than full so either an actual error or a calibration issue
        # return 100% and send an error message
        output_string = "ERROR: WaterLevelSensor - get_water_level - distance less than full"
        return(-1, output_string)
      elif distance > self.empty_distance:
        # the distance is more than empty so either an actual error or a calibration issue
        # return 0% and send an info message
        output_string = "ERROR: WaterLevelSensor - get_water_level - distance more than empty"
        return(-1, output_string)
      else:
        percentage = int(((self.empty_distance - distance) / (self.empty_distance - self.full_distance))*100)
        return(percentage, "Empty message")
    else:
      output_string = "ERROR: WaterLevelSensor - get_water_level - called when not active"
      return(-1, output_string)
