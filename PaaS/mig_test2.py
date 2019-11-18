import docker
import time
import os
from anytree import *
# Get docker client externally
client = docker.DockerClient(base_url='tcp://172.18.16.10:2375')

local_shared = {"/home/shubham/Desktop/Cloud-Term-Project/PaaS/shared": {'bind': '/home', 'mode': 'rw'}}

# dest client
dest_client = docker.from_env()

com4 = client.containers.get('com4')
com4.stop()
com4.remove()
dest_client.containers.run("cloudassignment/base", 
						command = ['home/rmq_com.py', 'rmq', 'exch3', 'exch4'],
						detach = True,    # If kept to false, will block the script. If script is killed, container exits 
						#devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
						entrypoint = ['python'],
						hostname = 'com4',
						name = 'com4',
						network = 'global_net',
						privileged = True,
						#publish_all_ports = True, #publish all ports to the host, so that we can send json data to it!
						stdin_open = True, # have to keep STDIN open to avoid container exit
						tty = True,		   # allocate pseudo tty to avoid container exit
						volumes = local_shared #For ease, we will mount a common shared folder on all containers.
					  )

print("Migrated com4 -->")