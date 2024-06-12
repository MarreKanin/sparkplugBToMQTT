import os
import time
import random
import paho.mqtt.client as mqtt
import sparkplug_b_pb2 as sparkplug_pb
import sparkplug_b as sparkplug_pb

# Configuration from environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
GROUP_ID = "SparkplugBGroup"
NODE_ID = "Node1"
DEVICE_ID = "Device1"

# Previous temperature value
prev_temperature = None

# Callback for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print(f"Connection failed with code {rc}")

# Create an MQTT client instance
client = mqtt.Client()
client.on_connect = on_connect

# Set username and password
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Connect to the broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the loop
client.loop_start()

while True:
    try:
        # Create a Sparkplug B payload
        payload = sparkplug_pb.Payload()
        metric = payload.metrics.add()
        metric.name = "temperature"
        metric.alias = 1
        metric.timestamp = int(time.time() * 1000)
        metric.datatype = sparkplug_pb.MetricDataType.Double
        
        # Generate a random temperature value within 1 to 5 degrees of the previous temperature
        if prev_temperature is None:
            temperature = round(random.uniform(0, 100), 2)
        else:
            temperature = round(prev_temperature + random.uniform(-5, 5), 2)
            temperature = max(0, min(100, temperature))  # Ensure temperature stays within [0, 100] range
        
        metric.double_value = temperature
        
        # Update previous temperature value
        prev_temperature = temperature

        # Encode the payload
        payload_bytes = payload.SerializeToString()

        # Publish the payload to the MQTT broker
        topic = f"spBv1.0/{GROUP_ID}/DDATA/{NODE_ID}/{DEVICE_ID}"
        client.publish(topic, payload_bytes)

        # Sleep for a random interval between 1 and 10 seconds
        time.sleep(random.uniform(1, 10))
    except KeyboardInterrupt:
        # Stop the loop and disconnect
        client.loop_stop()
        client.disconnect()
        break