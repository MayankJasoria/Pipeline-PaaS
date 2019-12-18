# Pipeline-PaaS
This is a project built using Docker in which a system has been designed allowing users to build a pipeline of services and execute it on a distributed systenm by simply selecting the desired services and connecting them in the desired manner. The system monitors the workload of each physical machine and the workload of each container, so that in case a container (service) undergoes starvation in terms of allocated resources, it may be migrated to another physical machine within the system which can allocate the required resources.

The project can be executed by running `website.py` located in the `PaaS` folder

However, before launching, some configuration must be performed first:
- In the file config.py, the IP:PORT of all physical machines which are running docker should be mentioned in the clientList as `tcp://<IP-OF-CONSUL>:<PORT-OF-CONSUL>`...
- In each sych physical machine within a local area network, service discovery is required, which can be provided through consul.
	- One system must run Consul and expose it on a public IP:PORT
	- All systems must run `sudo dockerd --cluster-store <IP-OF-CONSUL>:<PORT-OF_CONSUL> --cluster-advertise <IP-OF-HOST>:<PORT-OF-DOCKER>`
	- The above may require techniques like port forwarding through tools like `ncat`
