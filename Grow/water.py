import datetime
import time
import sys
import socket

import json
from irrigation_system import IrrigationSystem

import paho.mqtt.client as mqtt
import ssl
import time

# --------------------------
# Configuration
# --------------------------

CLIENT_ID = "python-mqtt-client-" + str(time.time()) # Unique client ID
BROKER_HOSTNAME = "a85dc6f63e6945e0be49d9103eb3fb6b.s1.eu.hivemq.cloud"
PORT = 8883  # TLS port
USERNAME = "GrowControl"
PASSWORD = "Gr0wplants"


READ_INTERVAL_TIME = 900 #seconds - this is time delay between sensor readings - default to 3600 (60 mins)
    
irrigation_system = IrrigationSystem(False)

running = True  # Global flag to control loop execution

# --------------------------
# Old-style callback functions (3 arguments)
# --------------------------
def on_connect(client, userdata, flags, rc):
    # Subscribe to a topic
    client.subscribe("pzgrow/#", qos=1)
    irrigation_system.set_mqtt_client(client)
    output_message = f"INFO: water.py - on_connect - connected with result code {rc}"
    irrigation_system.publish_message_and_print("pzgrow/info", output_message)
    

def on_command_message(client, userdata, msg):
    
    # Check that the message is in the right format
    
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        output_message = "ERROR: water.py - on_command_message - could not parse message payload into JSON"
        irrigation_system.publish_message_and_print("pzgrow/error", output_message)
        
    # correct format so process 
    
    else:
        if irrigation_system.watering == True:
            output_message = "ERROR: water.py - on_command_message - could not parse message payload into JSON"
            irrigation_system.publish_message_and_print("pzgrow/error", output_message)
        else:
            output_message = "INFO: water.py - on_command_message - received - " + str(message_json["command"]["value"])
            irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            if message_json["command"]["value"] == "Update":
                irrigation_system.update()
                #output_message = "INFO: water.py - on_command_message - updated"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Settings":
                irrigation_system.publish_settings()
                #output_message = "INFO: water.py - on_command_message - output settings"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Increase watering time":
                irrigation_system.auto_water_seconds = irrigation_system.auto_water_seconds + 5
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - increased auto watering time to " + str(irrigation_system.auto_water_seconds)
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Decrease watering time":
                irrigation_system.auto_water_seconds = irrigation_system.auto_water_seconds - 5
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - decreased auto watering time to " + str(irrigation_system.auto_water_seconds)
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Increase watering threshold":
                irrigation_system.min_moisture = irrigation_system.min_moisture + 1
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - increased watering threshold " + str(irrigation_system.min_moisture)
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Decrease watering threshold":
                irrigation_system.min_moisture = irrigation_system.min_moisture - 1
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - increased watering threshold " + str(irrigation_system.min_moisture)
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Auto water on":
                irrigation_system.auto_water_status = True
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - auto water turned on"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Auto water off":
                irrigation_system.auto_water_status = False
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - auto water turned off"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Manual water c1":
                irrigation_system.manual_water_channel_1()
                #output_message = "INFO: water.py - on_command_message - ran manual water c1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Manual water c2":
                irrigation_system.manual_water_channel_2()
                #output_message = "INFO: water.py - on_command_message - ran manual water c2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Capture image":
                irrigation_system.capture_image()
                #output_message = "INFO: water.py - on_command_message - capture image"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c1":
                irrigation_system.set_channel_1_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c1":
                irrigation_system.set_channel_1_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c2":
                irrigation_system.set_channel_2_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c2":
                irrigation_system.set_channel_2_status(False)
                #output_message = "INFO: water.py - on_command_message - deactivated c2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c1m1":
                irrigation_system.set_channel_1_moisture_1_status(True)
                irrigation_system.set_channel_1_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c1m1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c1m1":
                irrigation_system.set_channel_1_moisture_1_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c1m1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c1m2":
                irrigation_system.set_channel_1_moisture_2_status(True)
                irrigation_system.set_channel_1_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c1m2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c1m2":
                irrigation_system.set_channel_1_moisture_2_status(False)
                irrigation_system.write_variables()
                #output_message = "Deactivated c1m2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c2m1":
                irrigation_system.set_channel_2_moisture_1_status(True)
                irrigation_system.set_channel_2_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c2m1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c2m1":
                irrigation_system.set_channel_2_moisture_1_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c2m1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c2m2":
                irrigation_system.set_channel_2_moisture_2_status(True)
                irrigation_system.set_channel_2_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated C2m2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c2m2":
                irrigation_system.set_channel_2_moisture_2_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c2m2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c1p1":
                irrigation_system.set_channel_1_pump_1_status(True)
                irrigation_system.set_channel_1_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c1p1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c1p1":
                irrigation_system.set_channel_1_pump_1_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c1p1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c1p2":
                irrigation_system.set_channel_1_pump_2_status(True)
                irrigation_system.set_channel_1_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c1p2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c1p2":
                irrigation_system.set_channel_1_pump_2_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c1p2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c2p1":
                irrigation_system.set_channel_2_pump_1_status(True)
                irrigation_system.set_channel_2_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c2p1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c2p1":
                irrigation_system.set_channel_2_pump_1_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c2p1"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Activate c2p2":
                irrigation_system.set_channel_2_pump_2_status(True)
                irrigation_system.set_channel_2_status(True)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - activated c2p2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Deactivate c2p2":
                irrigation_system.set_channel_2_pump_2_status(False)
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - deactivated c2p2"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c1m1 dry":
                irrigation_system.set_channel_1_moisture_1_dry()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c1m1 dry level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c1m1 wet":
                irrigation_system.set_channel_1_moisture_1_wet()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c1m1 wet level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c1m2 dry":
                irrigation_system.set_channel_1_moisture_2_dry()
                irrigation_system.write_variables()
                #output_message = "c1m2 dry level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c1m2 wet":
                irrigation_system.set_channel_1_moisture_2_wet()
                irrigation_system.write_variables()
                #output_message = "c1m2 wet level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c2m1 dry":
                irrigation_system.set_channel_2_moisture_1_dry()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c2m1 dry level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c2m1 wet":
                irrigation_system.set_channel_2_moisture_1_wet()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c2m1 wet level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c2m2 dry":
                irrigation_system.set_channel_2_moisture_2_dry()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c2m2 dry level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            elif message_json["command"]["value"] == "Set c2m2 wet":
                irrigation_system.set_channel_2_moisture_2_wet()
                irrigation_system.write_variables()
                #output_message = "INFO: water.py - on_command_message - c2m2 wet level set"
                #irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            else:
                output_message = "ERROR: water.py - on_command_message - command not recognised - " + message_json["command"]["value"]
                print(output_message)
                irrigation_system.publish_message_and_print("pzgrow/error", output_message)
            #irrigation_system.publish_status()

def loop():
    global running
    while running:
        
        # pring and publish a message to show that system is operational
        output_message = "INFO: water.py - loop - running"
        irrigation_system.publish_message_and_print("pzgrow/info", output_message)
            
        # check to see if the irrigation system is currently watering
        
        if irrigation_system.watering == False:
        
            # we are not currently watering so ask system to auto-water if needed
            
            irrigation_system.auto_water()
            
            # publish the latest status
            
            irrigation_system.publish_status()
            
        else:
            
            # we are watering at the moment so send message and do nothing
            
            output_message = "INFO: water.py - loop - system currently watering"
            irrigation_system.publish_message_and_print("pzgrow/info", output_message)
        
        # wait for read_internal_time seconds to avoid high processor load
        time.sleep(READ_INTERVAL_TIME)

def destroy():
    output_message = "INFO: water.py - destroy - closing connections"
    irrigation_system.publish_message_and_print("pzgrow/info", output_message)


# I have set BT to IPv4 so this is not required
# May not work with the Hive MQTT serverless unless I can get an IPV4 version of the address
# === Helper function to force IPv4 ===
#def ipv4_host(hostname):
#    return socket.gethostbyname(hostname)  # Returns IPv4 address

#broker = ipv4_host(BROKER_HOSTNAME)  # Force IPv4        
        
if __name__ == '__main__':
    
    # --------------------------
    # Create MQTT client
    # --------------------------
    client = mqtt.Client(client_id=CLIENT_ID)

    # Set callbacks
    client.on_connect = on_connect
    client.message_callback_add("pzgrow/command", on_command_message)
    
    #client.on_command_message = on_command_message

    # Enable TLS
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)

    # Set username/password
    client.username_pw_set(USERNAME, PASSWORD)

    # Connect to broker
    client.connect(BROKER_HOSTNAME, PORT, keepalive=60)
    
    # Start the network loop
    client.loop_start()

    # Keep running to receive messages
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
    finally:
        output_message = "INFO - water - main - cleaned up - exiting"
        irrigation_system.publish_message_and_print("pzgrow/info", output_message)
        client.loop_stop()
        client.disconnect()
        destroy()

