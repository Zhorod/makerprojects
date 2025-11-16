import RPi.GPIO as GPIO
import time
import datetime
import sys
#import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt

from picamera import PiCamera

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
MQTT_HOSTNAME = "a85dc6f63e6945e0be49d9103eb3fb6b.s1.eu.hivemq.cloud"
#MQTT_HOSTNAME = "broker.hivemq.com"
#MQTT_HOSTNAME = "test.mosquitto.org"
MIN_MOISTURE = 95 # minimum moisture precentage before watering
AUTO_WATER_SECONDS = 20 # default number of seconds to water for when auto watering
MANUAL_WATER_SECONDS = 10 # default number of seconds to water for when manual watering
EMPTY_WATER_DISTANCE = 20 # default for empty water distance
FULL_WATER_DISTANCE = 4 # default for full water distance
WATER_LOW = 20 # percent below which the system wont water to save the pumps
VARIABLE_FILENAME = "/home/mirror/GrowFiles/grow_variables.txt"

class IrrigationSystem:
  
  def __init__(self, auto_water_status):
    self.auto_water_status = auto_water_status;
    self.manual_water_seconds = MANUAL_WATER_SECONDS
    self.auto_water_seconds = AUTO_WATER_SECONDS
    self.watering = False
    self.mqtt_client = None
    
    try:
      GPIO.setmode(GPIO.BOARD) #numbers GPIOs by physical location)
    except:
      self.publish_message("pzgrow/info","INFO: IrrigationSystem - init - GPIO model already set")

    # create athe two channels
    # pins and ADC channels hard coded
    
    self.channel_1 = self.IrrigationSystemChannel("1", False,7,11,0,1)
    self.channel_2 = self.IrrigationSystemChannel("2", False,13,15,2,3)
    self.water_level = WaterLevelSensor(True,16,18,FULL_WATER_DISTANCE,EMPTY_WATER_DISTANCE)
    
    # when starting both channels and all sensors and pumps are not active
    
    self.set_channel_1_moisture_1_status(False)
    self.set_channel_1_moisture_2_status(False)
    self.set_channel_1_pump_1_status(False)
    self.set_channel_1_pump_2_status(False)
    self.set_channel_2_moisture_1_status(False)
    self.set_channel_2_moisture_2_status(False)
    self.set_channel_2_pump_1_status(False)
    self.set_channel_2_pump_2_status(False)
    
    # set min moisture to default
    self.min_moisture = MIN_MOISTURE 
    
    # update the water level reading
    self.water_level_value = 0 # define water level value
    self.water_level_value = self.water_level.get_water_level()
    
    # read the variables from file
    # if there is no variable file then the defaults are used and a new file is created
    if self.read_variables() == False:
      self.write_variables()
      
    # update moisture readings
    #self.channel_1.update()
    #self.channel_2.update()
    
    # publish status
    #self.publish_status()
   
    
  def __del__(self):
    GPIO.cleanup()
    return(True)
    
  def set_mqtt_client(self, mqtt_client):
    self.mqtt_client = mqtt_client
    self.channel_1.set_mqtt_client(mqtt_client)
    self.channel_2.set_mqtt_client(mqtt_client)
    
    
  def publish_message(self, topic, output_string):
    # this function publishes the message as is i.e. with no additional time stape - used for indicators rather than text notifications
    try:
      #mqtt_publish.single(topic, output_string, hostname=MQTT_HOSTNAME)
      self.mqtt_client.publish(topic, output_string,qos=1)
    except:
      error_message = "ERROR: IrrigationSystem - publish_message - error in mqtt publish - " + str(output_string) + " - at time " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      print(error_message)
    time.sleep(0.1) # delay to allow published message to be read
    
  def print_message(self, output_string):
    output_message = output_string +  " - at time " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    print(output_string)
    time.sleep(0.1) # delay to allow published message to be read
    sys.stdout.flush()
  
  def publish_message_and_print(self, topic, output_string):
    # this function publishes and prints the message with a time stamp added for textual notifications
    output_message = output_string +  " - at time " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    try:
      self.mqtt_client.publish(topic, output_message,qos=1)
      #mqtt_publish.single(topic, output_message, hostname=MQTT_HOSTNAME)
    except:
      error_message = "ERROR: IrrigationSystem - publish_message - error publishing - " + str(output_string) + " - at time " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      print(error_message)
    print(output_message)
    time.sleep(0.1) # delay to allow published message to be read
    sys.stdout.flush()
    
  def publish_status(self):
    self.publish_message("pzgrow/wl-status", self.water_level.active)
    self.publish_message("pzgrow/c1-status", self.channel_1.active)
    self.publish_message("pzgrow/c2-status", self.channel_2.active)
    self.publish_message("pzgrow/c1m1-status", self.channel_1.moisture_1.active)
    self.publish_message("pzgrow/c1m2-status", self.channel_1.moisture_2.active)
    self.publish_message("pzgrow/c1p1-status", self.channel_1.pump_1.active)
    self.publish_message("pzgrow/c1p2-status", self.channel_1.pump_2.active)
    self.publish_message("pzgrow/c2m1-status", self.channel_2.moisture_1.active)
    self.publish_message("pzgrow/c2m2-status", self.channel_2.moisture_2.active)
    self.publish_message("pzgrow/c2p1-status", self.channel_2.pump_1.active)
    self.publish_message("pzgrow/c2p2-status", self.channel_2.pump_2.active)
    self.publish_message("pzgrow/c1m1", self.channel_1.moisture_1_value)
    self.publish_message("pzgrow/c1m2", self.channel_1.moisture_2_value)
    self.publish_message("pzgrow/c1mav", self.channel_1.moisture_combined_value)
    self.publish_message("pzgrow/c2m1", self.channel_2.moisture_1_value)
    self.publish_message("pzgrow/c2m2", self.channel_2.moisture_2_value)
    self.publish_message("pzgrow/c2mav", self.channel_2.moisture_combined_value)
    self.publish_message("pzgrow/wl", self.water_level_value)
    self.publish_message("pzgrow/wl-status", self.water_level.active)
      
  def capture_image(self):
    try:
      camera = PiCamera()
      now = time.localtime(time.time())
      filename = '/home/mirror/Desktop/Images/image -'+ time.strftime("%c", now)+'.jpg'
      camera.rotation = 180
      camera.capture(filename)
    
      output_string = "INFO: IrrigationSystem - capture_image - captured image"
      self.publish_message_and_print("pzgrow/info",output_string)
    except:
      output_string = "ERROR: IrrigationSystem - capture_image - error when trying to capture image"
      self.publish_message_and_print("pzgrow/error",output_string)
    
    camera.close()
    
  def write_variables(self):
    
    # write variables to file
    
    # try to open the variable file
    try:
        variable_file = open(VARIABLE_FILENAME,"w")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        output_string = "ERROR: IrrigationSystem - write_variables - error opening file " + VARIABLE_FILENAME
        self.publish_message_and_print("pzgrow/error",output_string)
        return false
        
    # write the parameters
    variable_file.write("%i %i %i %i %s %s %s %s %s %i %i %i %i %s %s %s %s %s %i %i %i %s %i %i\n" % (
      self.channel_1.moisture_1.raw_min,
      self.channel_1.moisture_1.raw_max,
      self.channel_1.moisture_2.raw_min,
      self.channel_1.moisture_2.raw_max,
      str(self.channel_1.active),
      str(self.channel_1.moisture_1.active),
      str(self.channel_1.moisture_2.active),
      str(self.channel_1.pump_1.active),
      str(self.channel_1.pump_2.active),
      self.channel_2.moisture_1.raw_min,
      self.channel_2.moisture_1.raw_max,
      self.channel_2.moisture_2.raw_min,
      self.channel_2.moisture_2.raw_max,
      str(self.channel_2.active),
      str(self.channel_2.moisture_1.active),
      str(self.channel_2.moisture_2.active),
      str(self.channel_2.pump_1.active),
      str(self.channel_2.pump_2.active),
      self.water_level.empty_distance,
      self.water_level.full_distance,
      self.water_level.active,
      self.auto_water_status,
      self.auto_water_seconds,
      self.min_moisture))
      
    variable_file.close()
    
    # update the panel with current status
    self.publish_status()
    
  def read_variables(self):
    
    # write variables to file
    
    # try to open the variable file
    try:
        variable_file = open(VARIABLE_FILENAME,"r")
    except:
        # there was a problem opening the log file
        # write a message to stdout
        output_string = "ERROR: IrrigationSystem - read_variables - error opening file " + VARIABLE_FILENAME
        self.publish_message_and_print("pzgrow/error", output_string)
        return False
        
    # read the parameters
    values = variable_file.read().split()
    self.channel_1.moisture_1.raw_min = int(values[0])
    self.channel_1.moisture_1.raw_max = int(values[1])
    self.channel_1.moisture_2.raw_min = int(values[2])
    self.channel_1.moisture_2.raw_max = int(values[3])
    if(values[4] == "True"):
      self.set_channel_1_status(True)
    else:
      self.set_channel_1_status(False)
    if(values[5] == "True"):
      self.set_channel_1_moisture_1_status(True)
    else:
      self.set_channel_1_moisture_1_status(False)
    if(values[6] == "True"):
      self.set_channel_1_moisture_2_status(True)
    else:
      self.set_channel_1_moisture_2_status(False)
    if(values[7] == "True"):
      self.set_channel_1_pump_1_status(True)
    else:
      self.set_channel_1_pump_1_status(False)
    if(values[8] == "True"):
      self.set_channel_1_pump_2_status(True)
    else:
      self.set_channel_1_pump_2_status(False)
    self.channel_2.moisture_1.raw_min = int(values[9])
    self.channel_2.moisture_1.raw_max = int(values[10])
    self.channel_2.moisture_2.raw_min = int(values[11])
    self.channel_2.moisture_2.raw_max = int(values[12])
    if(values[13] == "True"):
      self.set_channel_2_status(True)
    else:
      self.set_channel_2_status(False)
    if(values[14] == "True"):
      self.set_channel_2_moisture_1_status(True)
    else:
      self.set_channel_2_moisture_1_status(False)
    if(values[15] == "True"):
      self.set_channel_2_moisture_2_status(True)
    else:
      self.set_channel_2_moisture_2_status(False)
    if(values[16] == "True"):
      self.set_channel_2_pump_1_status(True)
    else:
      self.set_channel_2_pump_1_status(False)
    if(values[17] == "True"):
      self.set_channel_2_pump_2_status(True)
    else:
      self.set_channel_2_pump_2_status(False)
    self.water_level.empty_distance = int(values[18])
    self.water_level.full_distance = int(values[19])
    self.water_level.active = int(values[20])
    if(values[21] == "True"):
      self.auto_water_status = True
    else:
      self.auto_water_status = False
    self.auto_water_seconds = int(values[22])
    self.min_water = int(values[23])
    
    variable_file.close()
    
    # update the values
    #self.update()
    
    # update the panel with current status
    #self.publish_status()

  def set_min_moisture(self, min_moisture):
    if min_moisture != self.min_moisture:
      self.min_moisture = min_moisture
      self.channel_1.min_moisture = self.min_moisture
      self.channel_2.min_moisture = self.min_moisture
      output_string = "INFO: IrrigationSystem - set_min_moisture - min moisture set to " + str(self.min_moisture)
      self.publish_message_and_print("pzgrow/info", output_string)
  
  def manual_water_channel_1(self):
    if self.watering == True:
      output_string = "INFO: IrrigationSystem - manual_water_channel_1 - already watering"
      self.publish_message_and_print("pzgrow/info", output_string)
      return(False)
    else:
      if self.water_level_value > WATER_LOW:
        # there is enough water, so water
        self.watering = True
        return_value = self.channel_1.manual_water(self.manual_water_seconds)
        self.update()
        self.watering = False
        if return_value == True:
          return(True)
        else:
          output_string = "ERROR: IrrigationSystem - manual_water_channel_1 - there was an error when manual watering"
          self.publish_message_and_print("pzgrow/error", output_string)
          return(False)
      else:
        output_string = "ERROR: IrrigationSystem - manual_water_channel_1 - not enough water - " + self.water_level_value
        self.publish_message_and_print("pzgrow/error", output_string)
        return(False)
        
  def manual_water_channel_2(self):
    if self.watering == True:
      output_string = "INFO: IrrigationSystem - manual_water_channel_ - already watering"
      self.publish_message_and_print("pzgrow/info", output_string)
      return(False)
    else:
      if self.water_level_value > WATER_LOW:
        # there is enough water, so water
        self.watering = True
        return_value = self.channel_2.manual_water(self.manual_water_seconds)
        self.update()
        self.watering = False
        if return_value == True:
          return(True)
        else:
          output_string = "ERROR: IrrigationSystem - manual_water_channel_2 - there was an error when manual watering"
          self.publish_message_and_print("pzgrow/error", output_string)
          return(False)
      else:
        output_string = "ERROR: IrrigationSystem - manual_water_channel_2 - not enough water - " + self.water_level_value
        self.publish_message_and_print("pzgrow/error", output_string)
        return(False)
  
  def update(self):
    self.water_level_value = self.water_level.get_water_level()
    self.channel_1.update()
    self.channel_2.update()
    self.publish_status()
    
  def auto_water(self):
    # update all stored sensors values and decide if watering is required
    
    if self.watering == False:
      
      # im not in the process of watering - pumps not running
          
      self.update()

      if self.auto_water_status == True:
        
        # autowater is on
        
        if self.water_level_value > WATER_LOW:
          
          # there is enough water, so water
          
          return_value = True;
          if self.channel_1.active == True:
            
            # channel 1 is active, so water
          
            self.watering = True
            watering_flag = self.channel_1.auto_water(self.auto_water_seconds)
            if watering_flag == False:
              return_value = False
            self.watering = False
            if watering_flag == False:
              output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 1"
              self.publish_message_and_print("pzgrow/error", output_string)
          else:
            
            # channel 1 is not active, so water
            
            output_string = "INFO: IrrigationSystem - auto_water - channel 1 is not active"
            self.publish_message_and_print("pzgrow/info", output_string)
          if self.channel_2.active == True:
            
            # channel w is active, so water
          
            self.watering = True;
            watering_flag = self.channel_2.auto_water(self.auto_water_seconds)
            if watering_flag == False:
                return_value = False
            self.watering = False;
            if watering_flag == False:
              output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 2"
              self.publish_message_and_print("pzgrow/error", output_string)
          else:
            
            # channel 2 is not active, so water
            
            output_string = "INFO: IrrigationSystem - auto_water - channel 2 is not active"
            self.publish_message_and_print("pzgrow/info", output_string)
          return(return_value)
        else:
          output_string = "ERROR: IrrigationSystem - auto_water - not enough water - level is " + self.water_level_value
          self.publish_message_and_print("pzgrow/error", output_string)
          return(False)
      
    else:
      output_string = "INFO: IrrigationSystem - update - update paused as system currently watering"
      self.publish_message_and_print("pzgrow/info", output_string)
      
    return(False)
    
    output_string = "INFO: IrrigationSystem - auto_water - auto water not active"
    self.publish_message_and_print("pzgrow/info", output_string)
    
  def set_channel_1_status(self, status):
    self.publish_message("pzgrow/c1-status", status)
    self.channel_1.active = status
    if(status == False):
      
      # channel is inactive so set status of components to inactive
      
      self.channel_1.moisture_1.active = False
      #self.publish_message("pzgrow/c1m1-status", status)
      self.channel_1.moisture_2.active = False
      #self.publish_message("pzgrow/c1m2-status", status)
      self.channel_1.pump_1.active = False
      #self.publish_message("pzgrow/c1p1-status", status)
      self.channel_1.pump_2.active = False
      #self.publish_message("pzgrow/c1p2-status", status)

  def set_channel_2_status(self, status):
    #self.publish_message("pzgrow/c2-status", status)
    # set the status of the channel to status
    self.channel_2.active = status
    if(status == False):
      
      # channel is inactive so set status of components to inactive
      
      self.channel_2.moisture_1.active = False
      #self.publish_message("pzgrow/c2m1-status", status)
      self.channel_2.moisture_2.active = False
      #self.publish_message("pzgrow/c2m2-status", status)
      self.channel_2.pump_1.active = False
      #self.publish_message("pzgrow/c2p1-status", status)
      self.channel_2.pump_2.active = False
      #self.publish_message("pzgrow/c2p2-status", status)

  def set_channel_1_moisture_1_status(self, status):
    #self.publish_message("pzgrow/c1m1-status", status)
    self.channel_1.moisture_1.active = status
        
  def set_channel_1_moisture_2_status(self, status):
    #self.publish_message("pzgrow/c1m2-status", status)
    self.channel_1.moisture_2.active = status
   
  def set_channel_2_moisture_1_status(self, status):
    #self.publish_message("pzgrow/c2m1-status", status)
    self.channel_2.moisture_1.active = status
        
  def set_channel_2_moisture_2_status(self, status):
    #self.publish_message("pzgrow/c2m2-status", status)
    self.channel_2.moisture_2.active = status
   
  def set_channel_1_pump_1_status(self, status):
    #self.publish_message("pzgrow/c1p1-status", status)
    self.channel_1.pump_1.active = status
        
  def set_channel_1_pump_2_status(self, status):
    #self.publish_message("pzgrow/c1p2-status", status)
    self.channel_1.pump_2.active = status
   
  def set_channel_2_pump_1_status(self, status):
    #self.publish_message("pzgrow/c2p1-status", status)
    self.channel_2.pump_1.active = status
        
  def set_channel_2_pump_2_status(self, status):
    #self.publish_message("pzgrow/c2p2-status", status)
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
      self.moisture_1_value = -1
      self.moisture_2_value = -1
      self.moisture_combined_value = -1
      self.min_moisture = MIN_MOISTURE
      self.mqtt_client = None
    
    def set_mqtt_client(self, mqtt_client):
      self.mqtt_client = mqtt_client
       
    def publish_message_and_print(self, topic, output_string):
      output_message = output_string +  " - at time " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      try:
        self.mqtt_client.publish(topic, output_message,qos=1)
      except:
        print("ERROR: IrrigationSystem - publish_message_and_print - error in mqtt publish - '" + output_string + "' to '" + topic + "'")
      print(output_message)
      time.sleep(0.1) # delay to allow published message to be read
      sys.stdout.flush()
      
    def auto_water(self, seconds):
      if self.moisture_1.active == True or self.moisture_2.active == True:
        #one of the sensors is active so the combined value can be used
        if self.moisture_combined_value < self.min_moisture:
          # moisture is below threshold so water
          if self.pump_1.active == True:
            self.pump_1.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran pump 1  on channel " + self.name 
            self.publish_message_and_print("pzgrow/info", output_string)
            return(True)
          elif self.pump_2.active == True:
            self.pump_2.run_pump(seconds)
            output_string = "INFO: IrrigationSystemChannel - auto_water - ran pump 2 on channel " + self.name 
            self.publish_message_and_print("pzgrow/info", output_string)
            return(True)
          else:
            output_string = "ERROR: IrrigationSystemChannel - auto_water - no active pumps on channel " + self.name
            self.publish_message_and_print("pzgrow/error", output_string)
            return(False)
        else:
          return(True)
      else:
        output_string = "ERROR: IrrigationSystemChannel - auto_water - no active mositure sensor on channel " + self.name 
        self.publish_message_and_print("pzgrow/error", output_string)
        return(False)
            
    def manual_water(self, seconds):
      # get the moisture level
      # if moisture level is below min then water
      
      if self.pump_1.active == True:
        self.pump_1.run_pump(seconds)
        output_string = "INFO: IrrigationSystemChannel - manual_water - ran pump 1 on channel " + self.name
        self.publish_message_and_print("pzgrow/info", output_string)
        return(True)
      elif self.pump_2.active == True:
        self.pump_2.run_pump(seconds)
        output_string = "INFO: IrrigationSystemChannel - manual_water - ran pump 2 on channel " + self.name
        self.publish_message_and_print("pzgrow/info", output_string)
        return(True)
      else:
        output_string = "ERROR: IrrigationSystemChannel - manual_water - no active pumps on channel " + self.name
        self.publish_message_and_print("pzgrow/error", output_string)
        return(False)
    
    def update(self):
      
      if self.moisture_1.active == True and self.moisture_2.active == True:
        # both active, use 1
        self.moisture_1_value = self.moisture_1.get_moisture()
        self.moisture_2_value = self.moisture_2.get_moisture()
        self.moisture_combined_value = self.moisture_1_value
      elif self.moisture_1.active == True:
        # only moisture 1 sensor active
        self.moisture_1_value = self.moisture_1.get_moisture()
        self.moisture_combined_value = self.moisture_1_value
        self.moisture_2_value = -1
      elif self.moisture_2.active == True:
        # only moisture 2 sensor active
        self.moisture_2_value = self.moisture_2.get_moisture()
        self.moisture_combined_value = self.moisture_2_value
        self.moisture_1_value = -1
      else:
        self.moisture_1_value = -1
        self.moisture_2_value = -1
        self.moisture_combined_value = -1
        
