from statslib import statslib
import time

input = {
    'tcp://172.18.16.10:2375': ['rmq'],
    'tcp://localhost:2375': ['com0']
}
stats_obj = statslib(input)
stats_obj.start()

time.sleep(5)
print(stats_obj.stats['tcp://172.18.16.10:2375']['rmq']['cpu'])

stats_obj.addCont('tcp://localhost:2375', 'com4')
time.sleep(5)

print(stats_obj.stats['tcp://localhost:2375']['com4']['mem'])

stats_obj.deleteCont('tcp://localhost:2375', 'com0')

stats_obj.addCont('tcp://172.18.16.10:2375', 'com1')
stats_obj.addCont('tcp://172.18.16.10:2375', 'com2')
stats_obj.addCont('tcp://172.18.16.10:2375', 'com3')

time.sleep(8)
print(stats_obj.stats['tcp://172.18.16.10:2375']['com2']['mem'])

stats_obj.deleteCont('tcp://localhost:2375', 'com4')
stats_obj.deleteCont('tcp://172.18.16.10:2375', 'com1')
stats_obj.deleteCont('tcp://172.18.16.10:2375', 'com2')
stats_obj.deleteCont('tcp://172.18.16.10:2375', 'com3')
stats_obj.deleteCont('tcp://172.18.16.10:2375', 'rmq')

