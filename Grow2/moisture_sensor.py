import math
import datetime
import time
import sys
import statistics
import Adafruit_ADS1x15


import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client


#gain for adc - default to 1
GAIN=1

adc=Adafruit_ADS1x15.ADS1115()

class MoistureSensor:
  
  # define class variables - all instances share varaible
  
  def __init__(self, active, channel, gain, samples, raw_min, raw_max):
    
    # define instance variables
    
    self.raw_min = raw_min
    self.raw_max = raw_max
    self.samples = samples
    self.channel = channel
    self.gain = gain
    self.active = active
  
  def get_moisture(self):
    if (self.active == True):
      moisture_percent = 0
      moisture_reading = 0.0
      
      # take self.samples readings and use the median to determine a percentage using raw_min, raw_max and raw_range
      
      values = [0]*self.samples
      for i in range(self.samples):
        try:
          reading = adc.read_adc(self.channel, self.gain)
        except:
          output_string = "ERROR: MoistureSensor - get_moisture - a2d converter error"
          mqtt_publish.single("pzgrow/error", output_string, hostname="test.mosquitto.org")
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return(False)
        values[i] = reading
      
      # if we have been succesful, take the median
      
      moisture_reading = statistics.median(values)
      moisture_percent = (int)((1.0-(float)((moisture_reading-self.raw_min) / (self.raw_max - self.raw_min)))*100.0)
      
      # auto tune that tests if the percent is out of range and changes the raw_min raw_max
      # only concern is if there is a sensor error
      
      if moisture_percent < 0:
        moisture_percent = 0
        raw_max = moisture_reading
      elif moisture_percent > 100:
        moisture_percent = 100
        raw_min = moisture_reading
      
      return(moisture_percent)
    else:
      #output_string = "INFO: MoistureSensor - get_moisture - called when not active"
      #mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      #time.sleep(0.1) # delay to allow published message to be read
      #print(output_string)
      return(-1)

  def set_dry(self):
    if (self.active == True):
      moisture_reading = 0.0
      
      # take self.samples readings and use the median to determine a percentage using raw_min, raw_max
      
      values = [0]*self.samples
      for i in range(self.samples):
        try:
          reading = adc.read_adc(self.channel, self.gain)
        except:
          output_string = "ERROR: MoistureSensor - set_dry - a2d converter error"
          mqtt_publish.single("pzgrow/error", output_string, hostname="test.mosquitto.org")
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return(False)
        values[i] = reading
      
      # if we have been succesful, take the median
      
      moisture_reading = statistics.median(values)
      
      # set the max raw reading to current reading
      self.raw_max = moisture_reading
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - raw max set to %i" % (moisture_reading)
      mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
      Return(True)
    else:
      output_string = "ERROR: MoistureSensor - set_dry - called when not active"
      mqtt_publish.single("pzgrow/error", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
      return(False)

  def set_wet(self):
    if (self.active == True):
      moisture_reading = 0.0
      
      # take self.samples readings and use the median to determine a percentage using raw_min, raw_max and raw_range
      
      values = [0]*self.samples
      for i in range(self.samples):
        try:
          reading = adc.read_adc(self.channel, self.gain)
        except:
          output_string = "ERROR: MoistureSensor - set_wet - a2d converter error"
          mqtt_publish.single("pzgrow/error", output_string, hostname="test.mosquitto.org")
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return(False)
        values[i] = reading
      
      # if we have been succesful, take the median
      
      moisture_reading = statistics.median(values)
      
      # set the max raw reading to current reading
      self.raw_min = moisture_reading
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - raw min set to %i" % (moisture_reading)
      mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
    else:
      output_string = "INFO: MoistureSensor - set_wet - called when not active"
      mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)

  

  
  
# test the class works

#M1 = MoistureSensor(True, 0, GAIN, 100, 9500, 19500)
#M2 = MoistureSensor(True, 1, GAIN, 100, 9500, 19500)
#M3 = MoistureSensor(True, 2, GAIN, 100, 9500, 19500)
#M4 = MoistureSensor(True, 3, GAIN, 100, 9500, 19500)

#print(M1.get_moisture())
#print(M2.get_moisture())
#print(M3.get_moisture())
#print(M4.get_moisture())
