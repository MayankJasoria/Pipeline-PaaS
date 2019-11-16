import pika
import sys

arg_host = sys.argv[1]
arg_exchange = sys.argv[2]
arg_queue = sys.argv[3]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=arg_host))
channel = connection.channel()

channel.exchange_declare(exchange=arg_exchange, exchange_type='fanout')

result = channel.queue_declare(queue=arg_queue, exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=arg_exchange, queue=queue_name)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
