
import time
#import sys

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

from datetime import date
from datetime import datetime

from irrigation_system import IrrigationSystem

read_interval_time = 5 #seconds - this is time delay between sensor readings - default to 3600 (60 mins)

MQTT_HOSTNAME = "test.mosquitto.org"
    
irrigation_system = IrrigationSystem(False)

running = True  # Global flag to control loop execution

def loop(local_mqtt_client):
    global running
    while running:
        
        # check to see if the irrigation system is currently watering
        
        if irrigation_system.watering == False:
        
            # update the sensor value in the Irrigation System
            
            irrigation_system.update()
            
            # if auto water is active then auto water
            
            irrigation_system.auto_water()
            
        else:
            output_message = "INFO: water.py - loop - waiting as irrigation system currently watering"
            print(output_message)
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
        
        # wait for read_internal_time seconds to avoid high processor load
        
        time.sleep(read_interval_time)

def destroy():
    print("Closing connections")
    
def on_command_message(client, userdata, msg):
    
    # Check that the message is in the right format
    
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        output_message = "ERROR: water.py - on_command_message - could not parse message payload into JSON"
        print(output_message)
        mqtt_publish.single("pzgrow/error", output_message, hostname=MQTT_HOSTNAME)
      
    # correct format so process 
    
    else:
        if irrigation_system.watering == True:
            output_message = "ERROR: water.py - on_command_message - could not parse message payload into JSON"
            print(output_message)
            mqtt_publish.single("pzgrow/error", output_message, hostname=MQTT_HOSTNAME)
        else:
            output_message = "INFO: water.py - on_command_message - received " + str(message_json["command"]["value"]) + " at time " + str(message_json["command"]["time"])
            print(output_message)
            mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            if message_json["command"]["value"] == "Auto water on":
                irrigation_system.auto_water_status = True
                output_message = "INFO: water.py - on_command_message - auto water turned on"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Auto water off":
                irrigation_system.auto_water_status = False
                output_message = "INFO: water.py - on_command_message - auto water turned off"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Manual water c1":
                irrigation_system.manual_water_channel_1()
                output_message = "INFO: water.py - on_command_message - manual water c1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Manual water c2":
                irrigation_system.manual_water_channel_2()
                output_message = "INFO: water.py - on_command_message - manual water c2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c1":
                irrigation_system.set_channel_1_status(True)
                output_message = "INFO: water.py - on_command_message - activated c1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c1":
                irrigation_system.set_channel_1_status(False)
                output_message = "INFO: water.py - on_command_message - deactivated c1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c2":
                irrigation_system.set_channel_2_status(True)
                output_message = "INFO: water.py - on_command_message - activated c2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c2":
                irrigation_system.set_channel_2_status(False)
                output_message = "INFO: water.py - on_command_message - deactivated c2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c1m1":
                irrigation_system.set_channel_1_moisture_1_status(True)
                irrigation_system.set_channel_1_status(True)
                mqtt_publish.single("pzgrow/c1m1-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c1m1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c1m1":
                irrigation_system.set_channel_1_moisture_1_status(False)
                mqtt_publish.single("pzgrow/c1m1-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c1m1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c1m2":
                irrigation_system.set_channel_1_moisture_2_status(True)
                irrigation_system.set_channel_1_status(True)
                mqtt_publish.single("pzgrow/c1m2-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c1m2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c1m2":
                irrigation_system.set_channel_1_moisture_2_status(False)
                mqtt_publish.single("pzgrow/c1m2-status", False, hostname="test.mosquitto.org")
                output_message = "Deactivated c1m2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c2m1":
                irrigation_system.set_channel_2_moisture_1_status(True)
                irrigation_system.set_channel_2_status(True)
                mqtt_publish.single("pzgrow/c2m1-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c2m1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c2m1":
                irrigation_system.set_channel_2_moisture_1_status(False)
                mqtt_publish.single("pzgrow/c2m1-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c2m1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c2m2":
                irrigation_system.set_channel_2_moisture_2_status(True)
                irrigation_system.set_channel_2_status(True)
                mqtt_publish.single("pzgrow/c2m2-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated C2m2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c2m2":
                irrigation_system.set_channel_2_moisture_2_status(False)
                mqtt_publish.single("pzgrow/c2m2-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c2m2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c1p1":
                irrigation_system.set_channel_1_pump_1_status(True)
                irrigation_system.set_channel_1_status(True)
                mqtt_publish.single("pzgrow/c1p1-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c1p1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c1p1":
                irrigation_system.set_channel_1_pump_1_status(False)
                mqtt_publish.single("pzgrow/c1p1-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c1p1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c1p2":
                irrigation_system.set_channel_1_pump_2_status(True)
                irrigation_system.set_channel_1_status(True)
                mqtt_publish.single("pzgrow/c1p2-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c1p2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c1p2":
                irrigation_system.set_channel_1_pump_2_status(False)
                mqtt_publish.single("pzgrow/c1p2-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c1p2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c2p1":
                irrigation_system.set_channel_2_pump_1_status(True)
                irrigation_system.set_channel_2_status(True)
                mqtt_publish.single("pzgrow/c2p1-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c2p1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c2p1":
                irrigation_system.set_channel_2_pump_1_status(False)
                mqtt_publish.single("pzgrow/c2p1-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c2p1"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Activate c2p2":
                irrigation_system.set_channel_2_pump_2_status(True)
                irrigation_system.set_channel_2_status(True)
                mqtt_publish.single("pzgrow/c2p2-status", True, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - activated c2p2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Deactivate c2p2":
                irrigation_system.set_channel_2_pump_2_status(False)
                mqtt_publish.single("pzgrow/c2p2-status", False, hostname="test.mosquitto.org")
                output_message = "INFO: water.py - on_command_message - deactivated c2p2"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c1m1 dry":
                irrigation_system.set_channel_1_moisture_1_dry()
                output_message = "INFO: water.py - on_command_message - c1m1 dry level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c1m1 wet":
                irrigation_system.set_channel_1_moisture_1_wet()
                output_message = "INFO: water.py - on_command_message - c1m1 wet level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c1m2 dry":
                irrigation_system.set_channel_1_moisture_2_dry()
                output_message = "c1m2 dry level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c1m2 wet":
                irrigation_system.set_channel_1_moisture_2_wet()
                output_message = "c1m2 wet level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c2m1 dry":
                irrigation_system.set_channel_2_moisture_1_dry()
                output_message = "INFO: water.py - on_command_message - c2m1 dry level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c2m1 wet":
                irrigation_system.set_channel_2_moisture_1_wet()
                output_message = "INFO: water.py - on_command_message - c2m1 wet level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c2m2 dry":
                irrigation_system.set_channel_2_moisture_2_dry()
                output_message = "INFO: water.py - on_command_message - c2m2 dry level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            elif message_json["command"]["value"] == "Set c2m2 wet":
                irrigation_system.set_channel_2_moisture_2_wet()
                output_message = "INFO: water.py - on_command_message - c2m2 wet level set"
                mqtt_publish.single("pzgrow/info", output_message, hostname="test.mosquitto.org")
            else:
                output_message = "ERROR: water.py - on_command_message - command not recognised - " + message_json["command"]["value"]
                print(output_message)
                mqtt_publish.single("pzgrow/error", output_message, hostname="test.mosquitto.org")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("pzgrow/#", 0)
    
    
#def on_message(client, userdata, msg):
#    print(msg)
        
if __name__ == '__main__':
    
    try:
        local_mqtt_client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    except:
        local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.message_callback_add("pzgrow/command", on_command_message)
    
    local_mqtt_client.on_connect = on_connect
    #local_mqtt_client.on_message = on_message
    
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    local_mqtt_client.subscribe("pzgrow/#", 0)

    local_mqtt_client.loop_start()
    print("starting")
    
    try:
        loop(local_mqtt_client)
        
    except KeyboardInterrupt:
        print("interrupt received")
        running = False  # Stop the loop gracefully

    finally:
        destroy()
        local_mqtt_client.loop_stop()
        local_mqtt_client.disconnect()
        print("cleaned up - exiting")
