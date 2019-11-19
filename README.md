# Cloud-Term-Project
Cloud Computing Term Project

The project can be executed by running `website.py` located in the `PaaS` folder

However, before launching, some configuration must be performed first:
- In the file config.py, the IP:PORT of all physical machines which are running docker should be mentioned in the clientList as `tcp://172.17.16.10:2375`...
- In each sych physical machine within a local area network, service discovery is required, which can be provided through consul.
	- One system must run Consul and expose it on a public IP:PORT
	- All systems must run `sudo dockerd --cluster-store <IP-OF-CONSUL>:<PORT-OF_CONSUL> --cluster-advertise <IP-OF-HOST>:<PORT-OF-DOCKER>`
	- The above may require techniques like port forwarding through tools like `ncat`
