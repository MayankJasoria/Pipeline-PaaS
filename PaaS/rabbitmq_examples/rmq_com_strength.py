""" Stream communicator: Consumes from the given exchange identifier and produces 
    to a given one. 
    In RMQ queue name is not required. It is auto-generated, so we dont need to worry about it.
    Arguments: arg_exch_recv, arg_exch_send"""
import pika
import sys
import json

arg_host = sys.argv[1]
arg_exch_recv = sys.argv[2]
arg_exch_send = sys.argv[3]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=arg_host))

channel_recv = connection.channel()
channel_send = connection.channel()

#channel for receiving
channel_recv.exchange_declare(exchange=arg_exch_recv, exchange_type='fanout')
#channel for sending
channel_send.exchange_declare(exchange=arg_exch_send, exchange_type='fanout')

# declare recv queue
result = channel_recv.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# bind queue to the recv channel
channel_recv.queue_bind(exchange=arg_exch_recv, queue=queue_name)

# callback. Receives messages from channel_recv and sends to channel_send
def callback(ch, method, properties, body_recv):
    # In a non-trivial service, define what to do here. After doing it,
    # send it to channel_send. For communicator, we will just print and forward.
    #print(" [x] Received %r" % body_recv)
    dictr=json.loads(body_recv)
    #print(dictr)
    if float(dictr['strength']) >= 3 :
        print(" [x] Filtered %r" % body_recv)
        channel_send.basic_publish(exchange=arg_exch_send, routing_key='', body=body_recv)


channel_recv.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel_recv.start_consuming()
