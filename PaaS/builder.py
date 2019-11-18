import docker
import time
import os
from anytree import *

# init ID counter for unique ids for exchange identifiers
# format exch<exch_cnt>s
exch_cnt = 0

# init ID counter for unique ids for containers
# format exch<exch_cnt>s
cont_cnt = 0

# Construct a tree representing the pipeline

# First is always the consumer from rmq, we need to pass a producer and a 
root = Node("rmq_cons")
com0 = Node("com0", parent=root)

com1 = Node("com1", parent=com0)
com2 = Node("com2", parent=com0)
com3 = Node("com3", parent=com0)

com4 = Node("com4", parent=com2)

# print the tree
print(RenderTree(root, style=DoubleStyle))

# init pipeline

# Get a docker client
client = docker.from_env()

# Get docker client externally
client = docker.DockerClient(base_url='tcp://172.17.73.158:2375')

# Create a global network using Linux bridge driver 
global_net = client.networks.create("global_net", driver="bridge")

# Shared folder configuration: location of the folder on host containing the scripts
#shared = {os.getcwd() + os.path.sep + "shared": {'bind': '/home', 'mode': 'rw'}}

# C:\Users\Mayank\Documents\BITS\Cloud Computing\Assignments\Term Project\Cloud-Term-Project\PaaS\shared
shared = {r"C:\Users\Mayank\Documents\BITS\Cloud Computing\Assignments\Term Project\Cloud-Term-Project\PaaS\shared": {'bind': '/home', 'mode': 'rw'}}

# Launch a pipeline consisting of three containers, mqtt[-p 1883:1883, mqtt_cons.py] -> rmq_cons.py -> docker logs
container1 = client.containers.run("cloudassignment/rabbitmq",
						#command = '/bin/bash',
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						hostname = 'rmq',
						name = 'rmq',
						network = 'global_net',
						privileged = True,
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = shared #For ease, we will mount a common shared folder on all containers.
					  )

container2 = client.containers.run("eclipse-mosquitto",
						#command = '/bin/bash',
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						hostname = 'mqtt',
						name = 'mqtt',
						network = 'global_net',
						ports = {'1883/tcp': 1884, '9001/tcp': 9001},
						privileged = True,
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = shared #For ease, we will mount a common shared folder on all containers.
					  )

print(container1)
print(container2)
print("Started rmq and mqtt. Waiting for 10 seconds before starting dependent services.")
time.sleep(10)

container3 = client.containers.run("cloudassignment/mqtt", 
						command = ['home/mqtt_cons.py', 'mqtt','rmq','logs'],
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						entrypoint = ['python'],
						hostname = 'mqtt_cons',
						name = 'mqtt_cons',
						network = 'global_net',
						privileged = True,
						#publish_all_ports = True, #publish all ports to the host, so that we can send json data to it!
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = shared #For ease, we will mount a common shared folder on all containers.
					  )

container4 = client.containers.run("cloudassignment/base", 
						command = ['home/rmq_com.py', 'rmq','logs', 'exch'+str(exch_cnt)],
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						entrypoint = ['python'],
						hostname = 'cons',
						name = 'cons',
						network = 'global_net',
						privileged = True,
						#publish_all_ports = True, #publish all ports to the host, so that we can send json data to it!
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = shared #For ease, we will mount a common shared folder on all containers.
					  )                      

root.container = container4
root.exch_cons = 'logs'
root.exch_prod = 'exch'+str(exch_cnt)

print(container3)
print(container4)
print("Started mqtt_cons")
print("Started rmq_cons")   

print(container3)
print(container4)

print("Building tree...")
# Iterate the tree in pre-order ways
for node in PreOrderIter(com0):
    parent = node.parent
    exch_cnt = exch_cnt + 1
    node.exch_cons = parent.exch_prod
    node.exch_prod = 'exch'+str(exch_cnt)
    node.container = client.containers.run("cloudassignment/base", 
						command = ['home/rmq_com.py', 'rmq', parent.exch_prod, node.exch_prod],
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						entrypoint = ['python'],
						hostname = node.name,
						name = node.name,
						network = 'global_net',
						privileged = True,
						#publish_all_ports = True, #publish all ports to the host, so that we can send json data to it!
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = shared #For ease, we will mount a common shared folder on all containers.
					  )
    print(node.name)
    print(node.container)               

print("Send data stream to mqtt protocol at localhost:1884!!")

input("Press Enter to shut down the platform...")

print("Stopping containers...")
# Cleanup: close all the containers and remove the network

for node in PreOrderIter(com0):
    node.container.stop(timeout=1)

container4.stop(timeout=1)
container3.stop(timeout=1)
container2.stop(timeout=1)
container1.stop(timeout=1)

print("Removing containers...")
container4.remove()
container3.remove()
container2.remove()
container1.remove()

for node in PreOrderIter(com0):
    node.container.remove()

print("Removing network: global_net...")
global_net.remove()

print("Cleanup complete. Exiting...")                      
    





