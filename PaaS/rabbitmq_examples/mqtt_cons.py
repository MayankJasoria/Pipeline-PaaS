#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

# This is the Subscriber

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("/test")

def on_message(client, userdata, msg):
  print(msg.payload.decode())
  channel.basic_publish(exchange='logs', routing_key='', body=msg.payload.decode())
    
client = mqtt.Client()
client.connect("localhost",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()

