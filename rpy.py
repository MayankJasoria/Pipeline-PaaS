 ####################################################################
 # dummy_ctrl.py
 # This is a dummy script that acts like a controller. It lets a
 # user/tester send task requests to our task handler thread pool
 # and get results back
 ####################################################################
import threading
import json
import csv
import rabbitpy
#import mqsetup
import traceback
import sys
 
AMQP_URL='amqp://guest:guest@192.168.99.100:5672/%2f'
CTRL_EXCHANGE='exchange'
CTRL_QUEUE='queue'
CTRL_RESPONSE_QUEUE='resp_queue'
CTRL_ROUTING_KEY='rk'
CTRL_RESPONSE_ROUTING_KEY='resp_rk'

#CTRL_QUEUE=''
#CTRL_RESPONSE_QUEUE=''
#CTRL_ROUTING_KEY=''
#CTRL_RESPONSE_ROUTING_KEY=''

 #
 # This class listens for responses from our task thread pool program
 # When it gets a response message it just prints it
 #
class MQResponseListener(object):
    def __init__(self,queue_name=CTRL_RESPONSE_QUEUE):
        self.queue_name=queue_name
        self.running=False
        self.conn=None
        self.channel=None
        self.exchange=None
        self.queue=None

    #
    # This is the listener function that runs in an infinite loop in a thread.
    # It keeps going until the user stops it with a stop call
    #
    def run_listener(self):
        print "Running listener"
        with rabbitpy.Connection(AMQP_URL) as self.conn:
            # Open the channel to communicate with RabbitMQ
            print "Got self.conn"
            with self.conn.channel() as self.channel:
                print "Got self.channel"
                self.queue = rabbitpy.Queue(self.channel, self.queue_name)
                print "Got self.queue on queue name %s" % self.queue_name
                print "Finished listener setup, now wait for messages"

                for message in self.queue.consume():
                    if message:
                        print "***********************************************************************"
                        print "Received Message!"
                        print "***********************************************************************"
                        print "Message body is %s" % message.body
                        message.ack()
                        print "Waiting for next message"
                    else:
                        print "Message is None, did we just call stop consuming?"
                        break
                print "Finished consuming"

        print "End of run_listener"

    #
    # This launches the listener as a thread and then returns
    # The thread will run forever (persistent listener)
    #
    def start(self):
        self.thread=threading.Thread(target=self.run_listener)
        self.running=True
        print "Starting listener"
        self.thread.start()

    def stop(self):
        print "stopping consuming"
        self.running=False
        self.queue.stop_consuming()
        print "end of listener.stop()"

    def join(self):
        self.thread.join()

def publish_message(channel,body_value):
    #
    # Create the message to publish
    #
    message = rabbitpy.Message(channel, body_value)

    #
    # Publish the message, looking for the return value to be a bool True/False
    #
    if message.publish(CTRL_EXCHANGE, routing_key=CTRL_ROUTING_KEY, mandatory=True):
        print 'Message publish confirmed by RabbitMQ'
    else:
        print 'RabbitMQ indicates message publishing failure'
def setup():
     # Connect to RabbitMQ on localhost, port 5672 as guest/guest
     conn=rabbitpy.Connection(AMQP_URL)
     channel=conn.channel()

     exchange = rabbitpy.Exchange(channel, CTRL_EXCHANGE, exchange_type='direct')
     exchange.declare()

     queue = rabbitpy.Queue(channel, CTRL_QUEUE)
     queue.durable = True
     queue.declare()
     queue.bind(exchange, routing_key=CTRL_ROUTING_KEY)

     channel.close()
     conn.close()

     #########

     # Connect to RabbitMQ on localhost, port 5672 as guest/guest
     conn=rabbitpy.Connection(AMQP_URL)
     channel=conn.channel()

     exchange = rabbitpy.Exchange(channel, CTRL_EXCHANGE, exchange_type='direct')
     exchange.declare()

     queue2 = rabbitpy.Queue(channel, CTRL_RESPONSE_QUEUE)
     queue2.durable = True
     queue2.declare()
     queue2.bind(exchange, routing_key=CTRL_RESPONSE_ROUTING_KEY)

     channel.close()
     conn.close()

def set_args(arguments) :

    CTRL_QUEUE=arguments[0]
    CTRL_RESPONSE_QUEUE=arguments[1]
    CTRL_ROUTING_KEY=arguments[2]
    CTRL_RESPONSE_ROUTING_KEY=arguments[3]

if __name__ == '__main__':

    '''
    arguments = sys.argv[1:]
    count = len(arguments)
    if count<4 :
        print("4 arguments expected")
        sys.exit(1)
    else:
        print(arguments[0])
    '''
    #set_args(arguments)
    setup()

    listener=MQResponseListener()
    #listener.set_val(CTRL_RESPONSE_QUEUE)
    listener.start()

    with rabbitpy.Connection(AMQP_URL) as conn:
        # Open the channel to communicate with RabbitMQ
        with conn.channel() as channel:

            exchange = rabbitpy.Exchange(channel, CTRL_EXCHANGE, exchange_type='direct')
            exchange.declare()

            # Turn on publisher confirmations
            channel.enable_publisher_confirms()

            queue = rabbitpy.Queue(channel, CTRL_QUEUE)
            queue.durable = True
            queue.declare()

            queue.bind(exchange, routing_key=CTRL_ROUTING_KEY)

            #queue = rabbitpy.Queue(channel, CTRL_QUEUE)

            while True:
                print "Options:"
                print "1. Call function some_dummy_command"
                print "2. Quit"
                try:
                    opt=int(raw_input('Select option number:'))
                    if opt==1:
                        #
                        # create message body in cmdstr
                        #
                        print "Sending a message"
                        csv_rows = []
                        with open("beach-water-quality-automated-sensors-1.csv") as csvfile:
                            reader = csv.DictReader(csvfile)
                            field = reader.fieldnames
                            for row in reader:
                                csv_rows.extend([{field[i]:row[field[i]] for i in range(len(field))}])
                        
                        for d in csv_rows:
                            cmdstr=json.dumps(d)
                            publish_message(channel,cmdstr)
                        '''    
                        jsonfile=open("beach.json","r")
                        
                        for d in jsonfile :
                            cmdstr=json.dumps(d)
                            publish_message(channel,cmdstr)
                        
                        cmdDict={
                            'ids': ['id1', 'id2', 'id3'],
                            'name': "some_dummy_command",
                            'args': [],
                            'kwargs': {}
                        }
                        cmdstr=json.dumps(cmdDict)
                        
                        #
                        # publish message on channel
                        #
                        publish_message(channel,cmdstr)
                        '''
                    elif opt==2:
                        print "Stopping the listener"
                        listener.stop()
                        print "Breaking"
                        break
                    else:
                        print "opt unknown: %s" % opt

                except rabbitpy.exceptions.NotConsumingError:
                    break
                except ValueError:
                    print "Not a number"

    print "Waiting for listener thread to complete"
    listener.join()
    print "Done!"

####################################################################################
# mqsetup.py
# This module makes sure the exchanges, queues, etc all get set up in RabbitMQ.
# This is crucial if not already set up, has no effect if they are already set up.
####################################################################################
'''
import rabbitpy
from constants import (
    AMQP_URL,
    CTRL_EXCHANGE,
    CTRL_QUEUE,
    CTRL_RESPONSE_QUEUE,
    CTRL_ROUTING_KEY,
    CTRL_RESPONSE_ROUTING_KEY
)
'''
 