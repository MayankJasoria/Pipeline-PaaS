import docker
import time

# Get a docker client
client = docker.from_env()

# Create a global network using Linux bridge driver 
global_net = client.networks.create("global_net", driver="bridge")

# Shared folder configuration: location of the folder on host containing the scripts
shared = {r'C:\Users\Mayank\Documents\BITS\Cloud Computing\Assignments\Term Project\Cloud-Term-Project\PaaS\shared': {'bind': '/home', 'mode': 'rw'}}

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
						command = ['home/rmq_cons.py', 'rmq','logs', 'hello1'],
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


print(container3)
print(container4)
print("Started mqtt_cons")
print("Started rmq_cons")

print("Send data stream to mqtt protocol at localhost:1884!!")

input("Press Enter to shut down the platform...")

print("Stopping containers...")
# Cleanup: close all the containers and remove the network
container4.stop()
container3.stop()
container2.stop()
container1.stop()

print("Removing containers...")
container4.remove()
container3.remove()
container2.remove()
container1.remove()

print("Removing network: global_net...")
global_net.remove()

print("Cleanup complete. Exiting...")
# 

# first arg - container name/id/object, any of these work. We have object, we use it!
# With alias we can refer to mongo:port instead of ip:port, in the pipeline.
#global_net.connect(container1, aliases = ['mongo1'])
#global_net.connect(container2, aliases = ['mongo2'])

""" Now you might want to do 'sudo docker network ls' and see global_net in the bridge list!
	Also, do 'sudo docker network inspect global_net' and see mongo container in the list of containers! 
	Also, do 'sudo docker exec -it <Container ID/Name> /bin/bash' and 'cd home' and 'ls' to see your host folder
	as specfified in volumes argument in containers.run() mounted in /home!!! """




