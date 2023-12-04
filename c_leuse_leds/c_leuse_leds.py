from paho.mqtt import client as mqtt_client
from simple_rpc import Interface
import paho.mqtt.client as mqtt

broker = 'c-beam.cbrp3.c-base.org'
port = 1883
topic = "c_leuse/+"
client_id = 'c_leusen_leds'

print("Starting c_leusen_leds")
interface = Interface('/dev/ttyUSB0')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "c_leuse/led_pattern":
        # interface.method0(int(msg.payload.decode()))
        interface.method0(msg.payload)
        print(f"pattern {msg.payload.decode()} was set")

    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

