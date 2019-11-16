import pika
import sys

arg_host = sys.argv[1]
arg_exchange = sys.argv[2]
arg_queue = sys.argv[3]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=arg_host))
channel = connection.channel()

channel.exchange_declare(exchange=arg_exchange,
                         exchange_type='fanout')

#channel.queue_declare(queue='hello')

for i in range(0,10):
	channel.basic_publish(exchange=arg_exchange, routing_key='', body='Hello World!')
	print(" [x] Sent 'Hello World!'")

connection.close()
