import docker
import time

# Get a docker client
client = docker.from_env()

""" There are two ways of going about this, either:
	1. Create a network(s) first, and then init the containers, supplying the
	   network(s) as a function call arg to client.containers.run().
	   (https://docker-py.readthedocs.io/en/stable/containers.html)
	2. Init all containers first, and then use client.networks.connect(<Container>, args)
	   to connect them together. (https://docker-py.readthedocs.io/en/stable/networks.html) 
	
	#2 seems to be better"""

""" Create a docker network, connect all the containers in the pipeline to 
	the same network. Alternatively, create multiple networks for connecting 
	containers in a linear fashion instead of connecting them all together in
	a single network. But does the latter serve any purpose?"""


""" Returns a container object, if detach = True. 
	If detach is false, run() blocks and will return logs when script exits """
container = client.containers.run("mongo:latest", 
						command = '/bin/bash',
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						privileged = True,
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = {'/home/shubham/Desktop/shared': {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
					  )

print(container)

# Create a global network using Linux bridge driver 
global_net = client.networks.create("global_net", driver="bridge")

# first arg - container name/id/object, any of these work. We have object, we use it!
# With alias we can refer to mongo:port instead of ip:port, in the pipeline.
global_net.connect(container, aliases = ['mongo'])

""" Now you might want to do 'sudo docker network ls' and see global_net in the bridge list!
	Also, do 'sudo docker network inspect global_net' and see mongo container in the list of containers! 
	Also, do 'sudo docker exec -it <Container ID/Name> /bin/bash' and 'cd home' and 'ls' to see your host folder
	as specfified in volumes argument in containers.run() mounted in /home!!! """




