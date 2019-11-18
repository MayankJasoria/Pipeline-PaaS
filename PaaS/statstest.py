from statslib import statslib
import time

input = {
    'tcp://172.17.74.183:2375': ['rmq']
}
stats_obj = statslib(input)
stats_obj.start()

time.sleep(10)
print(stats_obj.stats['tcp://172.17.74.183:2375']['rmq']['cpu'])