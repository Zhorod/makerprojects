# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time
import sys

def read_input(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    while True:
        safe_limit = 1.0
        try:
            direction, amount = input("Enter command and amount: ").split()
        except:
            print("Could not parse input")
        else:
            if direction == "r":
                direction = "right"
            if direction == "l":
                direction = "left"
            if direction == "b":
                direction = "back"
            if direction == "f":
                direction = "forward"
            print(direction, str(amount))
            if float(amount) <= safe_limit:
                qa_json = {"command": direction, "distance": amount}
                qa_string = json.dumps(qa_json)
                mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
                print("JSON published: ", qa_string)
            else:
                print("Amount above safe limit of: ", safe_limit)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    local_mqtt_client = mqtt_client.Client()
    #local_mqtt_client.message_callback_add("mydaemon/listen", on_listen_message)
    #local_mqtt_client.message_callback_add("mydaemon/look", on_look_message)
    # local_mqtt_client.on_connect = on_connect
    #local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    #local_mqtt_client.subscribe("mydaemon/#", 0)
    local_mqtt_client.loop_start()

    read_input('PyCharm')

    local_mqtt_client.loop_stop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
