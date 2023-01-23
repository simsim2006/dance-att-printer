# Import package
from escpos import printer
import paho.mqtt.client as mqtt
import ssl
import json
import io
from dotenv import load_dotenv
import os
from ast import literal_eval

load_dotenv()

# Define Variables
MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")
MQTT_HOST = os.environ.get("MQTT_HOST")
CA_ROOT_CERT_FILE = os.environ.get("CA_ROOT_CERT_FILE")
THING_CERT_FILE = os.environ.get("THING_CERT_FILE")
THING_PRIVATE_KEY = os.environ.get("THING_PRIVATE_KEY")
PRINTER_VENDOR_ID=literal_eval("0x"+os.environ.get("PRINTER_VENDOR_ID"))
PRINTER_PRODUCT_ID=literal_eval("0x"+os.environ.get("PRINTER_PRODUCT_ID"))

Epson = printer.Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)
Epson.hw('INIT')

# Define on connect event function
# We shall subscribe to our Topic in this function
def on_connect(mosq, obj, rc, e):
    print("Connected")
    Epson.text(os.environ.get("PRINTER_ID") + " ready")
    Epson.cut()
    mqttc.subscribe(MQTT_TOPIC, 0)

# Define on_message event function. 
# This function will be invoked every time,
# a new message arrives for the subscribed topic 
def on_message(mosq, obj, msg):
        print("Topic: " + str(msg.topic))
        print("QoS: " + str(msg.qos))
        print("Payload: " + str(msg.payload))
        try:
                jsonString = json.load(io.BytesIO(msg.payload.replace(b"'", b'"')))
                text = jsonString['toprint']

                text = text.replace("[center]", "\x1b\x61\x01")
                text = text.replace("[/center]", "\x1b\x61\x00")
                text = text.replace("[right]", "\x1b\x61\x02")
                text = text.replace("[/right]", "\x1b\x61\x00")
                text = text.replace("[left]", "\x1b\x61\x00")
                text = text.replace("[/left]", "\x1b\x61\x00")
                text = text.replace("[b]", "\x1b\x45\x01")
                text = text.replace("[/b]", "\x1b\x45\x00")
                text = text.replace("[br]", "\n")
                text = text.replace("[grand]", "\x1d\x21\x13")
                text = text.replace("[/grand]", "\x1b\x21\x00")
                text = text.replace("[petit]", "\x1b\x21\x00")
                text = text.replace("[/petit]", "\x1b\x21\x00")
                text = text.replace("[u]", "\x1b\x2d\x01")
                text = text.replace("[/u]", "\x1b\x2d\x00")
                text = text.replace("[line]", "------------------------------------------------\n")
                text = text.replace("[cut]", "\x1d\x56\x01")
                text = text.replace("[inverse]", "\x1d\x42\x01")
                text = text.replace("[/inverse]", "\x1d\x42\x00")
                text = text.replace("&euro;", "\x1bt\x10\x80\x1bt\x00")
                text = text.replace("&eacute;", "\x82")
                text = text.replace("&egrave;", "\x8A")
                text = text.replace("&ecirc;", "\x88")
                text = text.replace("&agrave;", "\x85")
                text = text.replace("&ecirc;", "\x88")
                text = text.replace("&deg;", "\x1bt\x10\xb0\x1bt\x00")
                text = text.replace("&ccedil;", "\x1bt\x10\xe7\x1bt\x00")
                text = text.replace("&euml;", "\x89")
                Epson.text(text)
                Epson.text("\n\n\n")
                Epson.cut()

                return;
        except:
                print("Could not print this")

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed to Topic: " + MQTT_TOPIC + " with QoS: " + str(granted_qos))

def on_disconnect(client, userdata,  rc):
    print("Disconnected")

# Initiate MQTT Client
mqttc = mqtt.Client(MQTT_TOPIC)

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect

# Configure TLS Set
mqttc.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, keyfile=THING_PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect with MQTT Broker
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

# Continue monitoring the incoming messages for subscribed topic
mqttc.loop_forever()