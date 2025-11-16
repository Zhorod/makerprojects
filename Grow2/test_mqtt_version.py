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
TOPIC = "test/topic"


# --------------------------
# Old-style callback functions (3 arguments)
# --------------------------
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to a topic
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# --------------------------
# Create MQTT client
# --------------------------
client = mqtt.Client(client_id=CLIENT_ID)

# Set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Enable TLS
client.tls_set(tls_version=ssl.PROTOCOL_TLS)

# Set username/password
client.username_pw_set(USERNAME, PASSWORD)

# Connect to broker
client.connect(BROKER_HOSTNAME, PORT, keepalive=60)

# Start the network loop
client.loop_start()

# --------------------------
# Publish a message
# --------------------------
result = client.publish(TOPIC, payload="Hello Hive MQTT!", qos=1)
print("Publish result:", result)

# Keep running to receive messages
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
