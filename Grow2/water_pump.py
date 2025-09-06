import RPi.GPIO as GPIO
import sys
import time

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client

# define defaults

RUN_PUMP_SECONDS = 1

class WaterPump:
  
  # define class variables - all instances share varaible
  
  def __init__(self, active_status, gpio_pin):
    
    # define instance variables
    self.active = active_status
    self.gpio_pin = gpio_pin
    
    # set GPIO mode
    
    try:
      GPIO.setmode(GPIO.BOARD) #numbers GPIOs by physical location)
    except:
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - GPIO model already set"
      mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
      
    # init instance variables
    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, GPIO.HIGH) # default to off

  def __del__(self):
    GPIO.output(self.gpio_pin, GPIO.HIGH)
    GPIO.cleanup()
    

  def run_pump(self, num_seconds):
    if (self.active == True):
      #output_string = "Water pump started"
      #mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      #time.sleep(0.1) # delay to allow published message to be read
      #print(output_string)
      GPIO.output(self.gpio_pin, GPIO.LOW)
      time.sleep(num_seconds)
      GPIO.output(self.gpio_pin, GPIO.HIGH)
      #output_string = "water pump stopped"
      #mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      #time.sleep(0.1) # delay to allow published message to be read
      #print(output_string)
      return(True)
    else:
      output_string = "ERROR: WaterPump - run_pump - called when not active"
      mqtt_publish.single("pzgrow/ERROR", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
      return(False)

# test the class works

#P1 = WaterPump(True, 7)
#P2 = WaterPump(True, 11)
#P3 = WaterPump(True, 13)
#P4 = WaterPump(True, 15)

#print(P1.run_pump(RUN_PUMP_SECONDS))
#print(P2.run_pump(RUN_PUMP_SECONDS))
#print(P3.run_pump(RUN_PUMP_SECONDS))
#print(P4.run_pump(RUN_PUMP_SECONDS))

