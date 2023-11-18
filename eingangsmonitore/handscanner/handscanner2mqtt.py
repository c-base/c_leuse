import serial
import time
import threading
from paho.mqtt import client as mqtt_client


broker = 'c-beam.cbrp3.c-base.org'
port = 1883
topic = "handscanner/touched"
client_id = 'handscanner_touch'

print("Starting handscanner2mqtt")

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect")
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    # client.connect_async(broker, port)
    return client



def touch_thread(client):
    touched = False
    print("Starting serial read loop")
    # with serial.Serial('/dev/ttyS0', 19200, timeout=0.2) as ser:
    with serial.Serial('/dev/ttyS0', 9600, timeout=0.1) as ser:
        while True:
            # if client:
            #     result = client.loop(1)
            # if not client: # or result != 0:
                # try:
                    # client = connect_mqtt()
                    # result = client.loop(1)
                # except Exception as e:
                    # print(e)
                
            try:
                x = ser.read()
                # x = ser.read(ser.in_waiting)
                # print(x)
                if x != b'':
                    if not touched:
                        touched = True
                        print("touching")
                        client.publish(topic, True)
                        # time.sleep(1)
                else:
                    if touched:
                        touched = False
                        print("released")
                        client.publish(topic, False)
            except Exception:
                pass
print("Waiting 10s")
time.sleep(10)
client = None
try:
    client = connect_mqtt()
except Exception as e:
    print(e)
        

# result = client.loop(1)

x = threading.Thread(target=touch_thread, args=(client,))
x.start()

# client.loop_forever()
while True:
    if client:
        client.loop(1)
    else:
        time.sleep(1)
        try:
            client = connect_mqtt()
        except Exception as e:
            print(e)

