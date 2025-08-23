#import RPi.GPIO as GPIO
import time
#import Adafruit_ADS1x15
#import math
#import datetime
#import sys

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

from datetime import date
from datetime import datetime

from irrigation_system import IrrigationSystem

read_interval_time = 3 #seconds - this is time delay between sensor readings - default to 3600 (60 mins)

moisture_data_file_name = "/home/mirror/GrowFiles/grow_moisture_data.txt"
moisture_log_file_name = "/home/mirror/GrowFiles/grow_log_data.txt"

def setup():
    write_log_message("setup complete")
        
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
    
irrigation_system = IrrigationSystem(False)

def loop(local_mqtt_client):
    
    while True:
        
        #moisture_0_percent = irrigation_system.get_moisture(0)
        #moisture_1_percent = irrigation_system.get_moisture(1)
        #print("Moisture on channel 0 is: " + str(moisture_0_percent))
        #print("Moisture on channel 1 is: " + str(moisture_1_percent))
        #mqtt_publish.single("pzgrow/moisture0", moisture_0_percent, hostname="test.mosquitto.org")
        #mqtt_publish.single("pzgrow/moisture1", moisture_1_percent, hostname="test.mosquitto.org")
        
        # update the sensor value in the Irrigation System
        
        irrigation_system.update()
        
        # if auto water is active then auto water
        
        irrigation_system.auto_water()

        
        # read the moisture values
        #moisture_0_percent = irrigation_system.get_moisture(0)
        #moisture_1_percent = irrigation_system.get_moisture(1)
        #print("Moisture on channel 0 is: " + str(moisture_0_percent))
        #print("Moisture on channel 1 is: " + str(moisture_1_percent))
        
        #mqtt_publish.single("pzgrow/moisture0", moisture_0_percent, hostname="test.mosquitto.org")
        #mqtt_publish.single("pzgrow/moisture1", moisture_1_percent, hostname="test.mosquitto.org")
        
        # print the moisture values to the moisture data file
        #write_data_file()
        #write_stdout()
        
        # wait for read_internal_time seconds to avoid high processor load
        time.sleep(read_interval_time)

def destroy():
    write_log_message("closing connections")
    GPIO.cleanup()
    
def on_command_message(client, userdata, msg):
    #print("received message in on_command_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        output_message = "ERROR: water.py - on_command_message - could not parse message payload into JSON"
        print(output_message)
        mqtt_publish.single("pzgrow/error", output_message, hostname="test.mosquitto.org")
        
    else:
        print("Received " + str(message_json["command"]["value"]) + " at time " + str(message_json["command"]["time"]))
        if message_json["command"]["value"] == "Auto water on":
            irrigation_system.set_auto_water_status(True)
            output_message = "Auto water turned on"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Auto water off":
            irrigation_system.set_auto_water_status(False)
            output_message = "Auto water turned off"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Manual water 1":
            irrigation_system.manual_water_channel1()
            output_message = "Manual water channel 1"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Manual water 2":
            irrigation_system.manual_water_channel2()
            output_message = "Manual water channel 2"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate moisture 1a":
            irrigation_system.set_channel1_primary_moisture_sensor_status(True)
            output_message = "Activated moisture 1a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate moisture 1a":
            irrigation_system.set_channel1_primary_moisture_sensor_status(False)
            output_message = "Deactivated moisture 1a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate moisture 1b":
            irrigation_system.set_channel1_secondary_moisture_sensor_status(True)
            output_message = "Activated moisture 1b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate moisture 1b":
            irrigation_system.set_channel1_secondary_moisture_sensor_status(False)
            output_message = "Deactivated moisture 1b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate moisture 2a":
            irrigation_system.set_channel2_primary_moisture_sensor_status(True)
            output_message = "Activated moisture 2a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate moisture 2a":
            irrigation_system.set_channel2_primary_moisture_sensor_status(False)
            output_message = "Deactivated moisture 2a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate moisture 2b":
            irrigation_system.set_channel2_secondary_moisture_sensor_status(True)
            output_message = "Activated moisture 2b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate moisture 2b":
            irrigation_system.set_channel2_secondary_moisture_sensor_status(False)
            output_message = "Deactivated moisture 2b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate pump 1a":
            irrigation_system.set_channel1_primary_water_pump_status(True)
            output_message = "Activated pump 1a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate pump 1a":
            irrigation_system.set_channel1_primary_water_pump_status(False)
            output_message = "Deactivated pump 1a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate pump 1b":
            irrigation_system.set_channel1_secondary_water_pump_status(True)
            output_message = "Activated pump 1b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate pump 1b":
            irrigation_system.set_channel1_secondary_water_pump_status(False)
            output_message = "Deactivated pump 1b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate pump 2a":
            irrigation_system.set_channel2_primary_water_pump_status(True)
            output_message = "Deactivated pump 2a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate pump 2a":
            irrigation_system.set_channel2_primary_water_pump_status(False)
            output_message = "Deactivated pump 2a"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate pump 2b":
            irrigation_system.set_channel2_secondary_water_pump_status(True)
            output_message = "Activated pump 2b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate pump 2b":
            irrigation_system.set_channel2_secondary_water_pump_status(False)
            output_message = "Deactivated pump 2b"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate channel 1":
            irrigation_system.set_channel1_active(True)
            output_message = "Activated channel 1"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate channel 1":
            irrigation_system.set_channel1_active(False)
            output_message = "Deactivated channel 1"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Activate channel 2":
            irrigation_system.set_channel2_active(True)
            output_message = "Activated channel 2"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        elif message_json["command"]["value"] == "Deactivate channel 2":
            irrigation_system.set_channel2_active(False)
            output_message = "Deactivated channel 2"
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        else:
            output_message = "ERROR: water.py - on_command_message - command not recognised - " + message_json["command"]["value"]
            print(output_message)
            mqtt_publish.single("pzgrow/error", output_message, hostname="test.mosquitto.org")

def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("pzgrow/#", 0)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    i = 0
    # print(msg.topic+" "+str(msg.payload))

    
if __name__ == '__main__':
    
    # run set up
    setup()
    try:
        local_mqtt_client = mqtt_client.Client(mqttClient.CallbackAPIVersion.VERSION2)
    except:
        local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.message_callback_add("pzgrow/command", on_command_message)
    
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    local_mqtt_client.subscribe("pzgrow/#", 0)

    local_mqtt_client.loop_start()
    write_log_message("starting")

    try:
        loop(local_mqtt_client)
    except KeyboardInterrupt:
        write_log_message("interupt received")
    finally:
        destroy()
        local_mqtt_client.loop_stop()
        write_log_message("cleaned up - exiting")
