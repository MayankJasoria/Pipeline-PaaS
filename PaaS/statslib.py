from threading import Thread
import docker
import time
import json

class statslib:

    """ Receives a dictionary of docker clients -> list of containers  """
    def __init__(self, input):
        self.map = input
        self.stats = {} #stores the stats 

    def start(self):
        for client in self.map:
            for cont in self.map[client]:
                thread = Thread(target = self.stat_launch, args = (client, cont, ), daemon = True)
                thread.start()

    def stat_launch(self, client, cont):
        prevCPU = 0.0
        prevSystem = 0.0
        prev_tx_bytes = 0.0
        prev_time = 0.0
        cli = docker.APIClient(base_url=client)
        stats_obj = cli.stats(cont)
        for stat in stats_obj:
            curr_time = time.time()
            data = json.loads("".join( chr(x) for x in stat))
            cpu = self.calcCPUPercent(prevCPU, prevSystem, data)
            mem = (data['memory_stats']['usage']/data['memory_stats']['limit']) * 100.0
            # calculate net 
            tx_bytes = 0.0
            for intf in data['networks']:
                tx_bytes += data['networks'][intf]['tx_bytes']
            delt = curr_time - prev_time
            net = self.calcNet(prev_tx_bytes, tx_bytes, delt, 1000000.0)
            # store current stats
            prevCPU = data['cpu_stats']['cpu_usage']['total_usage']
            prevSystem = data['cpu_stats']['system_cpu_usage']
            prev_tx_bytes = tx_bytes
            prev_time = time.time()
            # calculate vol
            rvol = (1-cpu/100) * (1 - mem) * (1 - net)
            vol = 1/rvol
            #print('CPU USAGE: ' + str(cpu) + ' MEM: ' + str(mem) + ' NET: ' + str(net) + ' VOL: ' + str(vol))
            # set this in the member variables 
            self.stats.setdefault(client, {})
            self.stats[client].setdefault(cont, {})
            self.stats[client][cont]['cpu'] = cpu
            self.stats[client][cont]['mem'] = mem
            self.stats[client][cont]['net'] = net
            self.stats[client][cont]['vol'] = vol


    def calcCPUPercent(self, previousCPU, previousSystem, v):
        cpuPercent = 0.0
        # calculate the change for the cpu usage of the container in between readings
        cpuDelta = v['cpu_stats']['cpu_usage']['total_usage'] - previousCPU
        # calculate the change for the entire system between readings
        systemDelta = v['cpu_stats']['system_cpu_usage'] - previousSystem
        if systemDelta > 0.0 and cpuDelta > 0.0:
            cpuPercent = (cpuDelta / systemDelta) * len(v['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0

        return cpuPercent

    def calcNet(self, previous_tx_bytes, curr_tx_bytes, delta_t, bw):
        tx_rate = (curr_tx_bytes - previous_tx_bytes)/delta_t
        return tx_rate/bw