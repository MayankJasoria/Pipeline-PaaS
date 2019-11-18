import psutil

# We mainly need to communicate this info from each PM to the master PM
# We will use Datagram sockets (UDP) on a specific port to launch this script
# which will periodically send resource usage data to the master
# Resource usage data is the vol calcuated at each pm
psutil.net_io_counters()
psutil.cpu_percent(interval=1)
psutil.virtual_memory().percent