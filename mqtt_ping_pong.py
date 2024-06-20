import paho.mqtt.client as mqtt
import csv
import time
import random

from datetime import datetime

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "mqtt/test"

connection_timestamp = None

# Initialize CSV writer
with open('timestamps.csv', mode='w') as file:
    writer = csv.writer(file)
    writer.writerow(["SendDate", "ReceiveDate", "Delay", "Type"])

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code "+str(rc))
    # Subscribe to the topic for receiving messages
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global connection_timestamp
    print("Received message: " + msg.topic + " " + str(msg.payload))
    if msg.payload.decode() == "ping":
        print("Ping received")
        # Calculate the time since the ping was sent
        now = time.time()
        ping_ms = int((now - connection_timestamp) * 1000)
        print(f"Ping timestamp: {ping_ms} milisseconds")
        # Write to CSV
        with open('timestamps.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.fromtimestamp(connection_timestamp), datetime.fromtimestamp(now), ping_ms, "ping"])
            file.close()
    elif msg.payload.decode() == "pong":
        print("Pong received")
        # Calculate the time since the pong was sent
        now = time.time()
        pong_ms = int((now - connection_timestamp) * 1000)
        print(f"Pong timestamp: {pong_ms} milisseconds")
        # Write to CSV
        with open('timestamps.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.fromtimestamp(connection_timestamp), datetime.fromtimestamp(now), pong_ms, "pong"])
            file.close()

# Client 1 - Ping
ping_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
ping_client.on_connect = on_connect
ping_client.on_message = on_message
ping_client.connect(BROKER, PORT, 60)  # Replace with your MQTT server address and port
ping_client.loop_start()

# Client 2 - Receiver
pong_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
pong_client.on_connect = on_connect
pong_client.on_message = on_message
pong_client.connect(BROKER, PORT, 60)  # Replace with your MQTT server address and port
pong_client.loop_start()

# Keep the script running to listen for messages
while True:
    time.sleep(1)
    # Send "ping" message after connection
    connection_timestamp = time.time()
    ping_client.publish(TOPIC, "ping")

    # Send "pong" message after connection
    connection_timestamp = time.time()
    pong_client.publish(TOPIC, "pong")
