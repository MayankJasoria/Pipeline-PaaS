"""make .py file with global 'Getters' """

class Config:

    clientList = ['tcp://172.18.16.10:2375', 'tcp://172.18.16.54:2375', 'tcp://172.18.16.112:9350']

    shared = {
        clientList[0]: '/home/seekndestroy/Desktop/Cloud-Term-Project/PaaS/shared',
        clientList[1]: '/home/shubham/Desktop/Cloud-Term-Project/PaaS/shared',
        clientList[2]: '/home/nishat/Desktop/Cloud-Term-Project-master/PaaS/shared'
    }

    defaultClient = clientList[0]

    resources = {
        clientList[0]: {
            'cpu': 0.0055,
            'mem': 40.0,
            'net': 40.0
        },
        clientList[1]: {
            'cpu': 0.0055,
            'mem': 40.0,
            'net': 40.0
        },
        clientList[2]: {
            'cpu': 0.0055,
            'mem': 40.0,
            'net': 40.0
        }
    }

    services = {
        'strength':'rmq_com_strength.py',
        'action':'rmq_com_action.py',
        'style':'rmq_com_style.py',
        'weapon':'rmq_com_weapon.py',
        'input':'rmq_com_initial.py'
    }