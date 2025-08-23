import time
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client

from water_pump import WaterPump
from moisture_sensor import MoistureSensor

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
MANUAL_WATER_SECONDS = 3 # default number of seconds to water for when manual watering

class IrrigationSystem:
  
  def __init__(self, auto_water_status):
    self.auto_water_status = auto_water_status;
    self.manual_water_seconds = MANUAL_WATER_SECONDS
    self.auto_water_seconds = AUTO_WATER_SECONDS

    # create athe two channels
    
    self.channel1 = self.IrrigationSystemChannel("1", False,7,11,0,1)
    self.channel2 = self.IrrigationSystemChannel("2", False,13,15,2,3)
    
    
    # when starting both channels and all sensors and pumps are not active
    # set the dashboard flags
    
    mqtt_publish.single("pzgrow/m1a", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/m1b", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/m2a", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/m2b", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/p1a", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/p1b", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/p2a", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/p2b", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/channel1status", False, hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/channel2status", False, hostname=MQTT_HOSTNAME)
    

  def __del__(self):
    return(True)
  
  def update(self):
    
    # update each channel and publish values
    self.channel1.update()
    mqtt_publish.single("pzgrow/moisture1a", self.channel1.get_primary_moisture(), hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/moisture1b", self.channel1.get_secondary_moisture(), hostname=MQTT_HOSTNAME)
    
    self.channel2.update()
    mqtt_publish.single("pzgrow/moisture2a", self.channel2.get_primary_moisture(), hostname=MQTT_HOSTNAME)
    mqtt_publish.single("pzgrow/moisture2b", self.channel2.get_secondary_moisture(), hostname=MQTT_HOSTNAME)
    
  def manual_water_channel1(self):
    if self.channel1.manual_water(self.manual_water_seconds):
      return(True)
    else:
      output_string = "ERROR: IrrigationSystem - manual_water - there was an error when manual watering channel 1"
      mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
      print(output_string)
      return(False)

  def manual_water_channel2(self):
    if self.channel2.manual_water(self.manual_water_seconds):
      return(True)
    else:
      output_string = "ERROR: IrrigationSystem - manual_water - there was an error when manual watering channel 2"
      mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
      print(output_string)
      return(False)

  def auto_water(self):
    return_value = True
    if self.auto_water_status:
      if self.channel1.get_active():
        if self.channel1.auto_water(self.auto_water_seconds) == False:
          output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 1"
          mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          print(output_string)
          return_value = False
      else:
        output_string = "Channel 1 is not active"
        print(output_string)
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        return_value = True # do not want to raise an error though should not be called if not active
      if self.channel2.get_active():
        if self.channel2.auto_water(self.auto_water_seconds) == False:
          output_string = "ERROR: IrrigationSystem - auto_water - there was an error when auto watering on channel 2"
          print(output_string)
          mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          return_value = False
      else:
        output_string = "Channel 2 is not active"
        print(output_string)
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        time.sleep(0.1) # delay to allow published message to be read
        return_value = True # do not want to raise an error though should not be called if not active
    else:
      output_string = "Auto water not active"
      print(output_string)
      mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
      time.sleep(0.1) # delay to allow published message to be read
      return_value = False
    return(return_value)
    
  def set_auto_water_status(self, auto_water_status):
    self.auto_water_status = auto_water_status
  
  def get_auto_water_status(self):
    return(self.auto_water_status)
  
  def set_manual_water_seconds(self, seconds):
    self.manual_water_seconds = seconds
    
  def get_manual_water_seconds(self):
    return(self.manual_water_seconds)
    
  def set_auto_water_seconds(self, seconds):
    self.auto_water_seconds = seconds
    
  def get_auto_water_seconds(self):
    return(self.auto_water_seconds)
      
  def set_channel1_primary_moisture_sensor_status(self, status):
    mqtt_publish.single("pzgrow/m1a", status, hostname=MQTT_HOSTNAME)
    self.channel1.set_primary_moisture_sensor_status(status)
        
  def set_channel1_secondary_moisture_sensor_status(self, status):
    mqtt_publish.single("pzgrow/m1b", status, hostname=MQTT_HOSTNAME)
    self.channel1.set_secondary_moisture_sensor_status(status)
   
  def set_channel2_primary_moisture_sensor_status(self, status):
    mqtt_publish.single("pzgrow/m2a", status, hostname=MQTT_HOSTNAME)
    self.channel2.set_primary_moisture_sensor_status(status)
        
  def set_channel2_secondary_moisture_sensor_status(self, status):
    mqtt_publish.single("pzgrow/m2b", status, hostname=MQTT_HOSTNAME)
    self.channel2.set_secondary_moisture_sensor_status(status)
   
  def set_channel1_primary_water_pump_status(self, status):
    mqtt_publish.single("pzgrow/p1a", status, hostname=MQTT_HOSTNAME)
    self.channel1.set_primary_water_pump_status(status)
        
  def set_channel1_secondary_water_pump_status(self, status):
    mqtt_publish.single("pzgrow/p1b", status, hostname=MQTT_HOSTNAME)
    self.channel1.set_secondary_water_pump_status(status)
   
  def set_channel2_primary_water_pump_status(self, status):
    mqtt_publish.single("pzgrow/p2a", status, hostname=MQTT_HOSTNAME)
    self.channel2.set_primary_water_pump_status(status)
        
  def set_channel2_secondary_water_pump_status(self, status):
    mqtt_publish.single("pzgrow/p2b", status, hostname=MQTT_HOSTNAME)
    self.channel2.set_secondary_water_pump_status(status)
   
  def set_channel1_active(self, status):
    mqtt_publish.single("pzgrow/channel1status", status, hostname=MQTT_HOSTNAME)
    self.channel1.set_active(status)
        
  def set_channel2_active(self, status):
    mqtt_publish.single("pzgrow/channel2status", status, hostname=MQTT_HOSTNAME)
    self.channel2.set_active(status)
        
  # define an inner class called channel
  # a channel is instantiated with a fixed number of pumps / sensors
  
  class IrrigationSystemChannel:
    
    # define class variables - all instances share varaible
  
    def __init__(self, name, active, primary_pump_pin, secondary_pump_pin, primary_moisture_sensor_channel, secondary_moisture_sensor_channel):
      
      # define instance variables
      # all sensors and pumps start dissabled
      
      self.name = name
      self.active = active
      self.primary_water_pump = WaterPump(False, primary_pump_pin)
      self.secondary_water_pump = WaterPump(False, secondary_pump_pin)
      self.primary_moisture_sensor = MoistureSensor(False, primary_moisture_sensor_channel,GAIN, NUMBER_MOISTURE_SAMPLES, RAW_MOISTURE_MIN, RAW_MOISTURE_MAX)
      self.secondary_moisture_sensor = MoistureSensor(False, secondary_moisture_sensor_channel,GAIN, NUMBER_MOISTURE_SAMPLES, RAW_MOISTURE_MIN, RAW_MOISTURE_MAX)
      self.primary_moisture = -1
      self.secondary_moisture = -1
      self.min_moisture = MIN_MOISTURE
      
    def auto_water(self, seconds):
      
      if self.primary_moisture_sensor.get_active():
        if self.primary_moisture < self.min_moisture:
          # primary sensor is active and buffered value is below threshold so water
          if self.primary_water_pump.get_active():
            self.primary_water_pump.run_pump(seconds)
            output_string = "Ran primary pump on channel " + self.name 
            print(output_string)
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            return(True)
          elif self.secondary_water_pump.get_active():
            output_string = "Ran secondary pump on channel " + self.name 
            print(output_string)
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            self.secondary_water_pump.run_pump(seconds)
            return(True)
          else:
            output_string = "ERROR: IrrigationSystemChannel - auto_water - no active pumps on channel " + self.name
            print(output_string)
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            return(False)
        else:
          output_string = "Moisture > threshold on channel " + self.name 
          print(output_string)
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
          return(True)
      elif self.secondary_moisture_sensor.get_active():
        if self.secondary_moisture < self.min_moisture:
          if self.primary_water_pump.get_active():
            self.primary_water_pump.run_pump(seconds)
            output_string = "Ran primary pump on channel " + self.name 
            print(output_string)
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            return(True)
          elif self.secondary_water_pump.get_active():
            output_string = "Ran secondary pump on channel " + self.name
            print(output_string)
            mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            self.secondary_water_pump.run_pump(seconds)
            return(True)
          else:
            output_string = "ERROR: IrrigationSystemChannel - auto_water - no active pumps on channel " + self.name
            print(output_string)
            mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
            time.sleep(0.1) # delay to allow published message to be read
            return(False)
        else:
          output_string = "Moisture > threshold on channel " + self.name 
          print(output_string)
          mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
          time.sleep(0.1) # delay to allow published message to be read
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
      
      if self.primary_water_pump.get_active():
        output_string = "Using primary pump on channel " + self.name
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        self.primary_water_pump.run_pump(seconds)
        return(True)
      elif self.secondary_water_pump.get_active():
        output_string = "Using secondary pump on channel " + self.name
        mqtt_publish.single("pzgrow/info", output_string, hostname=MQTT_HOSTNAME)
        self.secondary_water_pump.run_pump(seconds)
        return(True)
      else:
        output_string = "ERROR: IrrigationSystemChannel - manual_water - no active pumps on channel " + self.name + " - returning primary moisture reading"
        mqtt_publish.single("pzgrow/error", output_string, hostname=MQTT_HOSTNAME)
        print(output_string)
        return(False)
    
    def update(self):
      if self.primary_moisture_sensor.get_active():
        self.primary_moisture = self.primary_moisture_sensor.get_moisture()
      if self.secondary_moisture_sensor.get_active():
        self.secondary_moisture = self.secondary_moisture_sensor.get_moisture()

    def get_primary_moisture(self):
      return(self.primary_moisture)

    def get_secondary_moisture(self):
      return(self.secondary_moisture)

    def set_primary_moisture_sensor_status(self, status):
      if status == False:
        self.primary_moisture = -1
      self.primary_moisture_sensor.set_active(status)
    
    def set_secondary_moisture_sensor_status(self, status):
      if status == False:
        self.secondary_moisture = -1
      self.secondary_moisture_sensor.set_active(status)
     
    def set_primary_water_pump_status(self, status):
      self.primary_water_pump.set_active(status)
    
    def set_secondary_water_pump_status(self, status):
      self.secondary_water_pump.set_active(status)
     
    def get_active(self):
      return(self.active)
    
    def set_active(self, status):
      self.active = status
      
#IS = IrrigationSystem(True)

#print(IS.get_moisture(0))
#print(IS.get_moisture(1))


