import paho.mqtt.client as mqtt
import csv
import time
import sys
import random

from datetime import datetime

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "mqtt/test"
MESSAGE = sys.argv[1]

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
    if msg.payload.decode() == "ping" and MESSAGE != "ping":
        print("Ping received")
        # Calculate the time since the ping was sent
        now = time.time()
        connection_ms = int((now - connection_timestamp) * 1000)
        print(f"Ping timestamp: {connection_ms} milisseconds")
        # Write to CSV
        with open('timestamps.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.fromtimestamp(connection_timestamp), datetime.fromtimestamp(now), connection_ms, "ping"])
            file.close()
    elif msg.payload.decode() == "pong" and MESSAGE != "pong":
        print("Pong received")
        # Calculate the time since the pong was sent
        now = time.time()
        connection_ms = int((now - connection_timestamp) * 1000)
        print(f"Pong timestamp: {connection_ms} milisseconds")
        # Write to CSV
        with open('timestamps.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.fromtimestamp(connection_timestamp), datetime.fromtimestamp(now), connection_ms, "pong"])
            file.close()

# Client 1 - Ping
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)  # Replace with your MQTT server address and port
mqtt_client.loop_start()

# Keep the script running to listen for messages
while True:
    time.sleep(1)
    # Send message after connection
    connection_timestamp = time.time()
    mqtt_client.publish(TOPIC, MESSAGE)
