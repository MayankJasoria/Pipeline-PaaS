from statthread import StatsThread
# from threading import Thread
# import multiprocessing
import docker
import time
import json

"""TODO: To define addCont(client, name) and deleteCont(client, name) 
         to launch a new stat thread or stop it and remove the cont name"""
class statslib:

    """ Receives a dictionary of docker clients -> list of containers  """
    def __init__(self, input):
        self.map = input
        self.stats = {} #stores**kwargs the stats 
        self.node_thread = {}

    def start(self):
        for client in self.map:
            self.node_thread.setdefault(client, {})
            for cont in self.map[client]:
                #self.node_thread[client].setdefault(cont, {})
                thread = StatsThread(target = self.stat_launch, args=(client, cont, ), daemon=True)
                thread.start()
                self.node_thread[client][cont] = thread


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
            time.sleep(1)


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

    def addCont(self, client, cont):
        """ Method to register a new container to an existing client so that it can be polled for statistics. """
        # add new value to list of containers in stats
        self.map[client].append(cont)

        # start a fresh process for this container
        thread = StatsThread(target=self.stat_launch, args = (client, cont, ))
        thread.start()
        self.node_thread[client][cont] = thread
        # [end of addCont]

    def deleteCont(self, client, cont):
        """ Method to unregister a container from an existing client so that it is no longer polled for statistics. """
        # stop thread associated with this container
        # process = self.node_proc[client][cont]
        # process.terminate()
        thread = self.node_thread[client][cont]
        thread.kill()

        # remove stats of container cont from this client
        self.stats[client][cont].pop('cpu', None)
        self.stats[client][cont].pop('mem', None)
        self.stats[client][cont].pop('net', None)
        self.stats[client][cont].pop('vol', None)
        self.stats[client].pop(cont, None)

        # remove container from list of containers in each client
        self.map[client].remove(cont)
        # [end of deleteCont]