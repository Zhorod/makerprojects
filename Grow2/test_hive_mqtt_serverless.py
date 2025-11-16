import paho.mqtt.client as paho
from paho import mqtt
import time
import ssl

# --- Configuration ---
# Replace with your HiveMQ Cloud details
BROKER_HOSTNAME = "a85dc6f63e6945e0be49d9103eb3fb6b.s1.eu.hivemq.cloud"
PORT = 8883 # Default secure port for MQTT over TLS
USERNAME = "GrowControl"
PASSWORD = "Gr0wplants"
TOPIC = "pzgrow/test"
CLIENT_ID = "python-mqtt-client-" + str(time.time()) # Unique client ID

# Callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to HiveMQ Cloud broker successfully!")
        client.subscribe(TOPIC, qos=1) # Subscribe upon successful connection
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

def on_publish(client, userdata, mid, reasonCodes, properties=None):
    print(f"Message {mid} published.")

# Create an MQTT client instance
client = paho.Client(
    client_id=CLIENT_ID,
    userdata=None,
    protocol=paho.MQTTv5,
    callback_api_version=paho.CallbackAPIVersion.v2
)

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Enable TLS for a secure connection
client.tls_set(tls_version=ssl.PROTOCOL_TLS)

# Set username and password
client.username_pw_set(USERNAME, PASSWORD)

# Connect to the broker
client.connect(BROKER_HOSTNAME, PORT, keepalive=60)

# Start the network loop
client.loop_start()

# Example: Publish a message every 5 seconds
try:
    while True:
        time.sleep(5)
        payload = "hot at " + time.strftime("%H:%M:%S")
        client.publish(TOPIC, payload=payload, qos=1)
except KeyboardInterrupt:
    print("Disconnecting...")
    client.disconnect()
    client.loop_stop()
