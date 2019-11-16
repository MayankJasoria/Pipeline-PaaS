import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

#channel.queue_declare(queue='hello')

for i in range(0,10):
	channel.basic_publish(exchange='logs', routing_key='', body='Hello World!')
	print(" [x] Sent 'Hello World!'")

connection.close()
