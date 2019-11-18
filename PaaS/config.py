"""make .py file with global 'Getters' """

class Config:

    clientList = ['tcp://172.18.16.10:2375', 'tcp://172.18.16.54:2375', 'tcp://172.18.16.112:2375']

    shared = {
        clientList[0]: '/home/seekndestroy/Desktop/Cloud-Term-Project/PaaS/shared',
        clientList[1]: '/home/shubham/Desktop/Cloud-Term-Project/PaaS/shared',
        clientList[2]: '/home/nishat/Desktop/Cloud-Term-Project-master/PaaS/shared'
    }

    defaultClient = clientList[0]

    resources = {
        clientList[0]: {
            'cpu': 
            'mem':
            'net':
        },
        clientList[1]: {
            'cpu': 
            'mem':
            'net':
        },,
        clientList[2]: {
            'cpu': 
            'mem':
            'net':
        }
    }