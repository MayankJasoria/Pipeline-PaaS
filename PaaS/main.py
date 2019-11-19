import docker
import time
from statslib import statslib
from anytree import *
from config import Config

class BuildPipeline:

    """ Class to collect all services in pipeline, then generate the tree """
    def __init__(self):
        self.ser_dict = {}
        self.root = None
        self.rootArgs = Node('rmq_cons')
        self.global_net = None
        self.shared = Config.shared
        self.container1 = None
        self.container2 = None
        self.container3 = None
        self.container4 = None
        self.real_clients = {}
        

        temp_dict = {}
        for cl in Config.clientList:
            temp_dict.setdefault(cl, [])
            self.real_clients[cl] = docker.DockerClient(base_url=cl)
        
        self.stats = statslib(temp_dict, self._migrate)

    def addService(self, name, service, parentName=None):
        """Registers a new service to be added to the pipeline.

        Keyword arguments:
        name       -- (string) Unique name given to the service by the user
        parentName -- (string) Name of the service whose output is treated as input by this service
                      Defaults to 'root' of the tree if not specified otherwise
        service    -- (string) The python file for the given service (say 'example.py')
        """
        if parentName == None:
            self.root = Node(name, parent=self.rootArgs)
            self.ser_dict[name] = self.root
            self.ser_dict[name].service = service
        else:
            self.ser_dict[name] = Node(name, parent=self.ser_dict[parentName])
            self.ser_dict[name].service = service

        # [end addService()]
        
    def removeService(self, name):
        """Unregisters a service which had been registered to be part of the pipeline.

        Keyword arguments:
        name -- (string) Name of the registered service which is to be removed
        """

        # remove if the name exists in dict
        self.ser_dict.pop(name, None)

        # [end removeService()]

    def buildPipeline(self, client=Config.defaultClient):
        """Builds the pipeline using the services registered in the dict."""

        # init ID counter for unique ids for exchange identifiers
        # format exch<exch_cnt>s
        exch_cnt = 0

        # init ID counter for un    def __sch_cb(self):
        # format exch<exch_cnt>s        pass
        cont_cnt = 0

        # Create a global network using Linux bridge driver 
        self.global_net = self.real_clients[client].networks.create("global_net", driver="overlay")


        # Launch a pipeline consisting of three containers, mqtt[-p 1883:1883, mqtt_cons.py] -> rmq_cons.py -> docker logs
        self.container1 = self.real_clients[client].containers.run("cloudassignment/rabbitmq",
                                #command = '/bin/bash',
                                detach = True,    # If kept to false, will block the script. If script is killed, container exits 
                                #devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
                                hostname = 'rmq',
                                name = 'rmq',
                                network = 'global_net',
                                privileged = True,
                                stdin_open = True, # have to keep STDIN open to avoid container exit
                                tty = True,		   # allocate pseudo tty to avoid container exit
                                volumes = {self.shared[client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )

        self.container2 = self.real_clients[client].containers.run("eclipse-mosquitto",
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
                                volumes = {self.shared[client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )

        print(self.container1)
        print(self.container2)
        print("Started rmq and mqtt. Waiting for 10 seconds before starting dependent services.")
        time.sleep(10)

        self.container3 = self.real_clients[client].containers.run("cloudassignment/mqtt", 
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
                                volumes = {self.shared[client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )

        self.container4 = self.real_clients[client].containers.run("cloudassignment/base", 
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
                                volumes = {self.shared[client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )                      

        self.rootArgs.container = self.container4
        self.rootArgs.exch_cons = 'logs'
        self.rootArgs.exch_prod = 'exch'+str(exch_cnt)

        print(self.container3)
        print(self.container4)
        print("Started mqtt_cons")
        print("Started rmq_cons")

        print("Building tree...")
        # Iterate the tree in pre-order ways
        for node in PreOrderIter(self.root):
            parent = node.parent
            exch_cnt = exch_cnt + 1
            node.exch_cons = parent.exch_prod
            node.exch_prod = 'exch'+str(exch_cnt)
            node.container = self.real_clients[client].containers.run("cloudassignment/base", 
                                command = ['home/' + self.ser_dict[node.name].service, 'rmq', parent.exch_prod, node.exch_prod],
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
                                volumes = {self.shared[client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )
            print(node.name)
            print(node.container)
            node.client = client
            self.stats.addCont(node.client, node.name)     

        print("Send data stream to mqtt protocol at localhost:1884!!")

        # [end buildPipeline()]

    def terminatePipeline(self):
        """Terminates the pipeline and performs cleanup"""
        print("Stopping containers...")
        # Cleanup: close all the containers and remove the network

        for node in PreOrderIter(self.root):
            self.stats.deleteCont(node.client, node.name)
            node.container.stop(timeout=1)

        self.container4.stop(timeout=1)
        self.container3.stop(timeout=1)
        self.container2.stop(timeout=1)
        self.container1.stop(timeout=1)

        print("Removing containers...")
        self.container4.remove()
        self.container3.remove()
        self.container2.remove()
        self.container1.remove()

        for node in PreOrderIter(self.root):
            node.container.remove()

        print("Removing network: global_net...")
        self.global_net.remove()

        self.stats.sch_thread.kill()
        print("Cleanup complete. Exiting...")

    # [end terminatePipeline()]

    def fetchStats(self):
        """Returns statistics to the user"""
        pass

    def _migrate(self, src_client, dest_client, cont):
        print("-- Migrating: src: " + src_client + " dest: " + dest_client+ " cont: " + cont)
        com0 = self.ser_dict[cont]
        com0.container.stop(timeout=1)
        com0.container.remove()
        com0.container = self.real_clients[dest_client].containers.run("cloudassignment/base", 
                                command = ['home/'+ self.ser_dict[cont].service, 'rmq', com0.parent.exch_prod, com0.exch_prod],
                                detach = True,    # If kept to false, will block the script. If script is killed, container exits 
                                #devices = ['/home/shubham/Desktop/shared:/home:rwm'], # This is used for mounting devices, not folders (volmes). So its wrong. Ignore.
                                entrypoint = ['python'],
                                hostname = com0.name,
                                name = com0.name,
                                network = 'global_net',
                                privileged = True,
                                #publish_all_ports = True, #publish all ports to the host, so that we can send json data to it!
                                stdin_open = True, # have to keep STDIN open to avoid container exit
                                tty = True,		   # allocate pseudo tty to avoid container exit
                                volumes = {self.shared[dest_client]: {'bind': '/home', 'mode': 'rw'}} #For ease, we will mount a common shared folder on all containers.
                            )