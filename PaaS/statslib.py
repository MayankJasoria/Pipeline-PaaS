from statthread import StatsThread
from config import Config
resources = Config.resources
del Config
# from threading import Thread
# import multiprocessing
import docker
import time
import json
from heapq import * 

class statslib:
    """ Statistics Library for container monitoring and orchestration. """
    
    def __init__(self, input, sch_cb):
        """
        Constructor for the statistics library 
            :param self: reference to this instance of the class
            :param input: dictionary of <docker clients> -> <list of containers>
            :param sch_cb: Name of the scheduler callback function for migration
        """   
        self.map = input
        self.stats = {} #stores**kwargs the stats 
        self.node_thread = {}
        for cl in input:
            self.node_thread.setdefault(cl, {})
            self.stats.setdefault(cl, {})
        self.sch_cb = sch_cb
        self.sch_thread = StatsThread(target = self.res_man, daemon=True)
        self.sch_thread.start()

    def start(self):
        for client in self.map:
            self.node_thread.setdefault(client, {})
            for cont in self.map[client]:
                #self.node_thread[client].setdefault(cont, {})
                thread = StatsThread(target = self.stat_launch, args=(client, cont, ), daemon=True)
                thread.start()
                self.node_thread[client][cont] = thread


    def stat_launch(self, client, cont):
        """
        Statistics polling thread for each container. Connects to the docker client
        running the container. Statistics flow into the stats_obj continously. 
        CPU, MEM and NET utilization are calculated every second and stored in
        self.stats.
            :param self: reference to this instance of the class
            :param client: docker client which is running the container
            :param cont: name of the container for which the statistics are obtained
        """ 

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
            mem = 0.0
            try:
                mem = (data['memory_stats']['usage']/data['memory_stats']['limit']) * 100.0
            except:
                pass    
            # calculate net 
            tx_bytes = 0.0
            try:
                for intf in data['networks']:
                    tx_bytes += data['networks'][intf]['tx_bytes']
            except:
                pass        
            delt = curr_time - prev_time
            net = self.calcNet(prev_tx_bytes, tx_bytes, delt, 1000000.0)
            # store current stats
            try:
                prevCPU = data['cpu_stats']['cpu_usage']['total_usage']
                prevSystem = data['cpu_stats']['system_cpu_usage']
            except:
                pass    
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

    def res_man(self):
        """ Resource scheduler. In every pass (every 2 seconds), calculates total cpu, mem and net utilization
            for all the physical machines. Calculates Manhattan distance of resource usage to max resource 
            available for each PM. In every pass migrates the container with highest vol in the target PM to the 
            PM with the lowest vol. The algorithm is therefore intended to ensure eventual balance of load amongst
            the PMs. 
        """

        while True:
            vol_map = []
            max_vol_cont_map = {}
            dist_map = []
            for client in self.stats:
                if len(self.stats[client]) == 0:
                    heappush(vol_map, (0, client))
                    continue
                max_vol_cont = None
                max_vol = 0
                cpu = 0
                mem = 0
                net = 0
                for cont in self.stats[client]:
                    cpu += self.stats[client][cont]['cpu']
                    mem += self.stats[client][cont]['mem']
                    net += self.stats[client][cont]['net']
                    if self.stats[client][cont]['vol'] > max_vol:
                        max_vol = self.stats[client][cont]['vol']
                        max_vol_cont = cont
                max_vol_cont_map[client] = max_vol_cont      
                rvol = (1-cpu) * (1-mem) * (1-net)
                vol = 1/rvol    
                dist = 0.0
                # check if this exceeds any of the resource limits:
                if resources[client]['cpu'] < cpu:
                    dist += cpu - resources[client]['cpu']
                    print(client + " cpu exceeded!!! val: " + str(cpu))

                if resources[client]['mem'] < mem:
                    dist += mem - resources[client]['mem']
                    print(client + " mem exceeded!!! val: " + str(mem))

                if resources[client]['net'] < net:
                    dist += net - resources[client]['net']
                    print(client + " net exceeded!!! val: " + str(net))

                if dist > 0:
                    heappush(dist_map, (-dist, client))
                heappush(vol_map, (vol, client))

                # print both lists here!
                print("VOL MAP: ")
                for ele in vol_map:
                    print(str(ele[0]) + " " + str(ele[1]))

                print("DIST MAP: ")
                for ele in dist_map:
                    print(str(ele[0]) + " " + str(ele[1]))
            
            if len(vol_map) > 0 and len(dist_map) > 0:
                dest_client = heappop(vol_map)[1]
                src_client = heappop(dist_map)[1]
                mig_cont = max_vol_cont_map[src_client]
                self.sch_cb(src_client, dest_client, mig_cont)

            time.sleep(2)

    
    def calcCPUPercent(self, previousCPU, previousSystem, v):
        """
        Calculates CPU utilization from stats obtained via docker API. 
        Inspired from 'docker stats'docstring here
            :param self: reference to this instance of the class
            :param previousCPU: previous total CPU usage
            :param previousSystem: previous system CPU usage
            :param v: current CPU data obtained via docker API
        """ 

        cpuPercent = 0.0
        try:
            # calculate the change for the cpu usage of the container in between readings
            cpuDelta = v['cpu_stats']['cpu_usage']['total_usage'] - previousCPU
            # calculate the change for the entire system between readings
            systemDelta = v['cpu_stats']['system_cpu_usage'] - previousSystem
            if systemDelta > 0.0 and cpuDelta > 0.0:
                cpuPercent = (cpuDelta / systemDelta) * len(v['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
        except:
            pass

        return cpuPercent

    def calcNet(self, previous_tx_bytes, curr_tx_bytes, delta_t, bw):
        """
        Calculates NET bandwidth
            :param self: reference to this instance of the class
            :param previous_tx_bytes: number of bytes transmitted as per previous stats
            :param curr_tx_bytes: number of bytes transmitted as per current stats
            :param delta_t: time interval between statistics collection
            :param bw: max bandwidth capacity on the container link
        """ 

        tx_rate = (curr_tx_bytes - previous_tx_bytes)/delta_t
        return tx_rate/bw

    def addCont(self, client, cont):
        """
        Register a new container to an existing client so that it can be polled for statistics.
            :param self: reference to this instance of the class
            :param client: docker client to which the container is to be registered
            :param cont: the name of the container to be registered
        """  

        # add new value to list of containers in stats
        self.map[client].append(cont)

        # start a fresh process for this container
        thread = StatsThread(target=self.stat_launch, args = (client, cont, ))
        thread.start()
        self.node_thread[client][cont] = thread
        # [end of addCont]

    def deleteCont(self, client, cont):
        """
        De-register a container from an existing client so that it is no longer polled for statistics.
            :param self: reference to this instance of the class
            :param client: docker client from which the container is to be de-registered
            :param cont: the name of the container to be de-registered
        """   

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