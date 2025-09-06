import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client

from water_pump import WaterPump
from moisture_sensor import MoistureSensor
from water_level_sensor import WaterLevelSensor

# set defaults

RAW_MOISTURE_MAX = 19500 # the default max for a moisture sensor - higher when dry
RAW_MOISTURE_MIN = 9500 # the default min for a moisture sensor - lower when moist
NUMBER_MOISTURE_SAMPLES = 100 # the default number of samples to take when measuring moisture
MAXIMUM_MOISTURE_DIFFERENCE = 10 # max perent difference between primary and secondary moisture sensors
EXPECTED_RANGE_MIN = -10 # percentage should not go below this unless an error or really poor calibration
EXPECTED_RANGE_MAX = 110 # percentage should not go above this unless an error or really poor calibration
GAIN = 1 # the adc gain
MQTT_HOSTNAME = "test.mosquitto.org"
MIN_MOISTURE = 70 # minimum moisture precentage before watering
AUTO_WATER_SECONDS = 3 # default number of seconds to water for when auto watering
MANUAL_WATER_SECONDS = 10 # default number of seconds to water for when manual watering
EMPTY_WATER_DISTANCE = 15 # default for empty water distance
FULL_WATER_DISTANCE = 5 # default for full water distance
VARIABLE_FILENAME = "/home/mirror/GrowFiles/grow_variables.txt"
MQTT_HOSTNAME = "test.mosquitto.org"

class IrrigationSystem:
  
  def __init__(self, auto_water_status):
    self.auto_water_status = auto_water_status;
    self.manual_water_seconds = MANUAL_WATER_SECONDS
    self.auto_water_seconds = AUTO_WATER_SECONDS
    self.watering = False
    
    try:
      GPIO.setmode(GPIO.BOARD) #numbers GPIOs by physical location)
    except:
      output_string = "INFO: IrrigationSystem - init - GPIO model already set"
      mqtt_publish.single("pzgrow/info", output_string, hostname="test.mosquitto.org")
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)

    # create athe two channels
    # pins and ADC channels hard coded
    
    self.channel_1 = self.IrrigationSystemChannel("1", True,7,11,0,1)
    self.channel_2 = self.IrrigationSystemChannel("2", True,13,15,2,3)
    self.water_level = WaterLevelSensor(True,16,18,FULL_WATER_DISTANCE,EMPTY_WATER_DISTANCE)
    
    # when starting both channels and all sensors and pumps are not active
    # set the dashboard flags
    
    #self.set_channel_1_status(True)
    #self.set_channel_2_status(False)
    self.set_channel_1_moisture_1_status(True)
    self.set_channel_1_moisture_2_status(True)
    self.set_channel_1_pump_1_status(True)
    self.set_channel_1_pump_2_status(True)
    self.set_channel_2_moisture_1_status(False)
    self.set_channel_2_moisture_2_status(False)
    self.set_channel_2_pump_1_status(False)
    self.set_channel_2_pump_2_status(False)
    
    mqtt_publish.single("pzgrow/wl-status", True, hostname=MQTT_HOSTNAME)
    
    # read the variables from file
    # if there is no variable file then the defaults are used
    self.read_variables()
    
  def __del__(self):
    GPIO.cleanup()
    return(True)
  
  def write_variables(self):
    
    # write variables to file
    
    # try to open the variable file
    try:
        variable_file = open(VARIABLE_FILENAME,"w")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        output_string = "ERROR: IrrigationSystem - write_variables - error opening file " + VARIABLE_FILENAME
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        time.sleep(0.1) # delay to allow published message to be read
        return false
        
    # write the parameters
    variable_file.write("%i %i %i %i %i %i %i %i %i %i\n" % (
      self.channel_1.moisture_1.raw_min,
      self.channel_1.moisture_1.raw_max,
      self.channel_1.moisture_2.raw_min,
      self.channel_1.moisture_2.raw_max,
      self.channel_2.moisture_1.raw_min,
      self.channel_2.moisture_1.raw_max,
      self.channel_2.moisture_2.raw_min,
      self.channel_2.moisture_2.raw_max,
      self.water_level.empty_distance,
      self.water_level.full_distance))
    
    variable_file.close()
    
  def read_variables(self):
    
    # write variables to file
    
    # try to open the variable file
    try:
        variable_file = open(VARIABLE_FILENAME,"r")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        output_string = "ERROR: IrrigationSystem - read_variables - error opening file " + VARIABLE_FILENAME
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        time.sleep(0.1) # delay to allow published message to be read
        return False
        
    # read the parameters
    numbers = variable_file.read().split()
    self.channel_1.moisture_1.raw_min = int(numbers[0])
    self.channel_1.moisture_1.raw_max = int(numbers[1])
    self.channel_1.moisture_2.raw_min = int(numbers[2])
    self.channel_1.moisture_2.raw_max = int(numbers[3])
    self.channel_2.moisture_1.raw_min = int(numbers[4])
    self.channel_2.moisture_1.raw_max = int(numbers[5])
    self.channel_2.moisture_2.raw_min = int(numbers[6])
    self.channel_2.moisture_2.raw_max = int(numbers[7])
    self.water_level.empty_distance = int(numbers[8])
    self.water_level.full_distance = int(numbers[9])
    
    variable_file.close()
    
  def update(self):
    
    # check to see if we are currently in a water cycle - required due to use of GPIO and threading
    
    if self.watering == False:
      # update the status of the channels, sensors and pumps
      
      mqtt_publish.single("pzgrow/wl-status", self.water_level.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1-status", self.channel_1.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2-status", self.channel_2.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1m1-status", self.channel_1.moisture_1.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1m2-status", self.channel_1.moisture_2.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1p1-status", self.channel_1.pump_1.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1p2-status", self.channel_1.pump_2.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2m1-status", self.channel_2.moisture_1.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2m2-status", self.channel_2.moisture_2.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2p1-status", self.channel_2.pump_1.active, hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2p2-status", self.channel_2.pump_2.active, hostname=MQTT_HOSTNAME)
      
      # update the waterlevel and publish values
      
      mqtt_publish.single("pzgrow/wl", self.water_level.get_water_level(), hostname=MQTT_HOSTNAME)
      
      # update each channel and publish values
      self.channel_1.update()
      mqtt_publish.single("pzgrow/c1m1", self.channel_1.moisture_1.get_moisture(), hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c1m2", self.channel_1.moisture_2.get_moisture(), hostname=MQTT_HOSTNAME)
      
      self.channel_2.update()
      mqtt_publish.single("pzgrow/c2m1", self.channel_2.moisture_1.get_moisture(), hostname=MQTT_HOSTNAME)
      mqtt_publish.single("pzgrow/c2m2", self.channel_2.moisture_2.get_moisture(), hostname=MQTT_HOSTNAME)
    else:
      output_string = "INFO: IrrigationSystem - update - update paused as system currently watering"
      mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
      print(output_string)
      time.sleep(0.1) # delay to allow published message to be read
    
  def manual_water_channel_1(self):
    if self.watering == True:
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - already watering"
      mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
      print(output_string)
      time.sleep(0.1) # delay to allow published message to be read
      return(False)
    else:
      self.watering = True
      return_value = self.channel_1.manual_water(self.manual_water_seconds)
      self.watering = False
      if return_value == True:
        return(True)
      else:
        output_string = "ERROR: IrrigationSystem - manual_water_channel_1 - there was an error when manual watering"
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        time.sleep(0.1) # delay to allow published message to be read
        return(False)

  def manual_water_channel_2(self):
    if self.watering == True:
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - already watering"
      mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
      print(output_string)
      time.sleep(0.1) # delay to allow published message to be read
      return(False)
    else:
      self.watering = True
      return_value = self.channel_2.manual_water(self.manual_water_seconds)
      self.watering = False
      if return_value == True:
        return(True)
      else:
        output_string = "ERROR: IrrigationSystem - manual_water_channel_2 - there was an error when manual watering"
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        time.sleep(0.1) # delay to allow published message to be read
        return(False)
    
  def auto_water(self):
    return_value = True
    if self.auto_water_status == True:
      if self.watering == True:
        return_value = False
        output_string = "INFO: IrrigationSystem - auto_water - already watering"
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        time.sleep(0.1) # delay to allow published message to be read
        return(return_value)
      else:
        if self.channel_1.active == True:
          self.watering = True
          return_value = self.channel_1.auto_water(self.auto_water_seconds)
          self.watering = False
          if return_value == False:
            output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 1"
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return_value = False
        else:
          output_string = "INFO: IrrigationSystem - auto_water - channel 1 is not active"
          print(output_string)
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          return_value = True # do not want to raise an error though should not be called if not active
        if self.channel_2.active == True:
          self.watering = True;
          return_value = self.channel_2.auto_water(self.auto_water_seconds) 
          self.watering = False;
          if return_value == False:
            output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 2"
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return_value = False
        else:
          output_string = "INFO: IrrigationSystem - auto_water - channel 2 is not active"
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return_value = True # do not want to raise an error though should not be called if not active
    else:
      output_string = "INFO: IrrigationSystem - auto_water - auto water not active"
      mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
      time.sleep(0.1) # delay to allow published message to be read
      print(output_string)
      return_value = False
      return(return_value)
    
  def set_channel_1_status(self, status):
    mqtt_publish.single("pzgrow/c1-status", status, hostname=MQTT_HOSTNAME)
    self.channel_1.active = status
    if(status == False):
      
      # channel is inactive so set status of components to inactive
      
      self.channel_1.moisture_1.active = False
      mqtt_publish.single("pzgrow/c1m1-status", status, hostname=MQTT_HOSTNAME)
      self.channel_1.moisture_2.active = False
      mqtt_publish.single("pzgrow/c1m2-status", status, hostname=MQTT_HOSTNAME)
      self.channel_1.pump_1.active = False
      mqtt_publish.single("pzgrow/c1p1-status", status, hostname=MQTT_HOSTNAME)
      self.channel_1.pump_2.active = False
      mqtt_publish.single("pzgrow/c1p2-status", status, hostname=MQTT_HOSTNAME)
        
  def set_channel_2_status(self, status):
    mqtt_publish.single("pzgrow/c2-status", status, hostname=MQTT_HOSTNAME)
    # set the status of the channel to status
    self.channel_2.active = status
    if(status == False):
      
      # channel is inactive so set status of components to inactive
      
      self.channel_2.moisture_1.active = False
      mqtt_publish.single("pzgrow/c2m1-status", status, hostname=MQTT_HOSTNAME)
      self.channel_2.moisture_2.active = False
      mqtt_publish.single("pzgrow/c2m2-status", status, hostname=MQTT_HOSTNAME)
      self.channel_2.pump_1.active = False
      mqtt_publish.single("pzgrow/c2p1-status", status, hostname=MQTT_HOSTNAME)
      self.channel_2.pump_2.active = False
      mqtt_publish.single("pzgrow/c2p2-status", status, hostname=MQTT_HOSTNAME)
  
  def set_channel_1_moisture_1_status(self, status):
    mqtt_publish.single("pzgrow/c1m1-status", status, hostname=MQTT_HOSTNAME)
    self.channel_1.moisture_1.active = status
        
  def set_channel_1_moisture_2_status(self, status):
    mqtt_publish.single("pzgrow/c1m2-status", status, hostname=MQTT_HOSTNAME)
    self.channel_1.moisture_2.active = status
   
  def set_channel_2_moisture_1_status(self, status):
    mqtt_publish.single("pzgrow/c2m1-status", status, hostname=MQTT_HOSTNAME)
    self.channel_2.moisture_1.active = status
        
  def set_channel_2_moisture_2_status(self, status):
    mqtt_publish.single("pzgrow/c2m2-status", status, hostname=MQTT_HOSTNAME)
    self.channel_2.moisture_2.active = status
   
  def set_channel_1_pump_1_status(self, status):
    mqtt_publish.single("pzgrow/c1p1-status", status, hostname=MQTT_HOSTNAME)
    self.channel_1.pump_1.active = status
        
  def set_channel_1_pump_2_status(self, status):
    mqtt_publish.single("pzgrow/c1p2-status", status, hostname=MQTT_HOSTNAME)
    self.channel_1.pump_2.active = status
   
  def set_channel_2_pump_1_status(self, status):
    mqtt_publish.single("pzgrow/c2p1-status", status, hostname=MQTT_HOSTNAME)
    self.channel_2.pump_1.active = status
        
  def set_channel_2_pump_2_status(self, status):
    mqtt_publish.single("pzgrow/c2p2-status", status, hostname=MQTT_HOSTNAME)
    self.channel_2.pump_2.active = status
   
  def set_channel_1_moisture_1_dry(self):
    self.channel_1.moisture_1.set_dry()
    self.write_variables()
    
  def set_channel_1_moisture_1_wet(self):
    self.channel_1.moisture_1.set_wet()
    self.write_variables()
    
  def set_channel_1_moisture_2_dry(self):
    self.channel_1.moisture_2.set_dry()
    self.write_variables()
    
  def set_channel_1_moisture_2_wet(self):
    self.channel_1.moisture_2.set_wet()
    self.write_variables()
  
  def set_channel_2_moisture_1_dry(self):
    self.channel_2.moisture_1.set_dry()
    self.write_variables()
    
  def set_channel_2_moisture_1_wet(self):
    self.channel_2.moisture_1.set_wet()
    self.write_variables()
    
  def set_channel_2_moisture_2_dry(self):
    self.channel_2.moisture_2.set_dry()
    self.write_variables()
    
  def set_channel_2_moisture_2_wet(self):
    self.channel_2.moisture_2.set_wet()
    self.write_variables()
   
      
  # define an inner class called IrrigationChannel
  # a channel is instantiated with 2 pumps and 2 sensors
  
  class IrrigationSystemChannel:
  
    def __init__(self, name, active, primary_pump_pin, secondary_pump_pin, primary_moisture_sensor_channel, secondary_moisture_sensor_channel):
      
      # define instance variables
      # all sensors and pumps start dissabled
      
      self.name = name
      self.active = active
      self.pump_1 = WaterPump(False, primary_pump_pin)
      self.pump_2 = WaterPump(False, secondary_pump_pin)
      self.moisture_1 = MoistureSensor(False, primary_moisture_sensor_channel,GAIN, NUMBER_MOISTURE_SAMPLES, RAW_MOISTURE_MIN, RAW_MOISTURE_MAX)
      self.moisture_2 = MoistureSensor(False, secondary_moisture_sensor_channel,GAIN, NUMBER_MOISTURE_SAMPLES, RAW_MOISTURE_MIN, RAW_MOISTURE_MAX)
      self.primary_moisture = -1
      self.secondary_moisture = -1
      self.min_moisture = MIN_MOISTURE
      
    def auto_water(self, seconds):
      
      if self.moisture_1.active == True:
        if self.primary_moisture < self.min_moisture:
          # primary sensor is active and buffered value is below threshold so water
          if self.pump_1.active == True:
            self.pump_1.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran primary pump on channel " + self.name 
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(True)
          elif self.pump_2.active == True:
            self.pump_2.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran secondary pump on channel " + self.name 
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(True)
          else:
            output_string = "ERROR: IrrigationSystemChannel - auto_water - no active pumps on channel " + self.name
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(False)
        else:
          output_string = "INFO: IrrigationSystemChannel - auto_water - moisture > threshold on channel " + self.name 
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return(True)
      elif self.moisture_2.active == True:
        if self.secondary_moisture < self.min_moisture:
          if self.pump_1.active == True:
            self.pump_1.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran primary pump on channel " + self.name 
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(True)
          elif self.pump_2.active == True:
            self.pump_2.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran secondary pump on channel " + self.name
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(True)
          else:
            output_string = "ERROR: IrrigationSystemChannel - auto_water - no active pumps on channel " + self.name
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            print(output_string)
            return(False)
        else:
          output_string = "INFO: IrrigationSystemChannel - auto_water - moisture > threshold on channel " + self.name 
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return(True)
      else:
        output_string = "ERROR: IrrigationSystemChannel - auto_water - no active mositure sensor on channel " + self.name 
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        print(output_string)
        return(False)
            
    def manual_water(self, seconds):
      # get the moisture level
      # if moisture level is below min then water
      
      if self.pump_1.active == True:
        output_string = "INFO: IrrigationSystemChannel - manual_water - using pump 1 on channel " + self.name
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        print(output_string)
        self.pump_1.run_pump(seconds)
        return(True)
      elif self.pump_2.active == True:
        output_string = "INFO: IrrigationSystemChannel - manual_water - using pump 2 on channel " + self.name
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        print(output_string)
        self.pump_2.run_pump(seconds)
        return(True)
      else:
        output_string = "ERROR: IrrigationSystemChannel - manual_water - no active pumps on channel " + self.name
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        print(output_string)
        return(False)
    
    def update(self):
      if self.moisture_1.active == True:
        self.primary_moisture = self.moisture_1.get_moisture()
      if self.moisture_2.active == True:
        self.secondary_moisture = self.moisture_2.get_moisture()
