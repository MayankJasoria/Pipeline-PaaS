#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pika
import sys
import time

arg_mqtt_host = sys.argv[1]
arg_host = sys.argv[2]
arg_exchange = sys.argv[3]

print(arg_host + " " + arg_exchange)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=arg_host))
channel = connection.channel()

channel.exchange_declare(exchange=arg_exchange,
                         exchange_type='fanout')

# This is the Subscriber

#while True:
#	time.sleep(2)

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("/test")

def on_message(client, userdata, msg):
  print(msg.payload.decode())
  channel.basic_publish(exchange=arg_exchange, routing_key='', body=msg.payload.decode())
    
client = mqtt.Client()
client.connect(arg_mqtt_host,1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()

