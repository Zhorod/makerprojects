# This file is the main element of the OODA service
# OODA stands for observe, orient, decide, act

import paho.mqtt.client as mqtt
import json
import time
import sys
import argparse


# specific callback function for message that have the topic "mydaemon/listen"
def on_listen_message(client, userdata, msg):
    print("received message in on_listen_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)
        if "utterance" in message_json and "time" in message_json:
            MyDaemonDecide_.unprocessed_utterances.append({"utterance":message_json["utterance"], "time":message_json["time"]})
            print("added new utterance " + message_json["utterance"] + " at time " + message_json["time"])
        else:
            print("the listen message had a missing key")

# specific callback function for message that have the topic "mydaemon/look"
def on_look_message(client, userdata, msg):
    print("received message in on_look_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)
        if "objects" in message_json and "time" in message_json:
            object_list = message_json["objects"]
            if len(object_list) > 0:
                MyDaemonDecide_.unprocessed_objects.insert(0,{"objects": object_list, "time": message_json["time"]})
                print("added new objects ", MyDaemonDecide_.unprocessed_objects[0])
        else:
            print("the look message had a missing key")
            
# specific callback function for message that have the topic "mydaemon/move"
def on_command_message(client, userdata, msg):
    print("received message in on_look_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    #message_text = msg.payload.decode('utf-8')
    #try:
    #    message_json = json.loads(message_text)
    #except Exception as e:
    #    print("Couldn't parse raw data: %s" % message_text, e)
    #else:
    #    print("JSON received : ", message_json)
    #    if "objects" in message_json and "time" in message_json:
    #        object_list = message_json["objects"]
    #        if len(object_list) > 0:
    #            MyDaemonDecide_.unprocessed_objects.insert(0,{"objects": object_list, "time": message_json["time"]})
    #            print("added new objects ", MyDaemonDecide_.unprocessed_objects[0])
    #    else:
    #        print("the look message had a missing key")

def on_message(client, userdata, msg):
    print("received message in on_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def decide(mqtt_client):
    while True:
        time.sleep(0.2)

def main():
    mqtt_client = mqtt.Client()  # create new instance
    #mqtt_client.message_callback_add("mydaemon/listen", on_listen_message)
    #mqtt_client.message_callback_add("mydaemon/look", on_look_message)
    mqtt_client.message_callback_add("pzgrow/command", on_command_message)
    mqtt_client.on_message = on_message
    mqtt_client.connect("test.mosquitto.org", 1883)  # connect to broker
    mqtt_client.subscribe("pzgrow/#", 0)

    mqtt_client.loop_start()
    decide(mqtt_client)
    mqtt_client.loop_stop()


if __name__ == '__main__':
    main()
