import threading
import trace
import sys
# class StatsThread(threading.Thread):

#     def __init__(self, target, *args, **kwargs):
#         super(StatsThread, self).__init__(target=target, *args, **kwargs)
#         self._stop = threading.Event()

#     # function using _stop function 
#     def stop(self): 
#         self._stop.set() 

#     def stopped(self): 
#         return self._stop.isSet() 
  
#     def run(self): 

class StatsThread(threading.Thread): 
  def __init__(self, *args, **keywords): 
    threading.Thread.__init__(self, *args, **keywords) 
    self.killed = False
  
  def start(self): 
    self.__run_backup = self.run 
    self.run = self.__run       
    threading.Thread.start(self) 
  
  def __run(self): 
    sys.settrace(self.globaltrace) 
    self.__run_backup() 
    self.run = self.__run_backup 
  
  def globaltrace(self, frame, event, arg): 
    if event == 'call': 
      return self.localtrace 
    else: 
      return None
  
  def localtrace(self, frame, event, arg): 
    if self.killed: 
      if event == 'line': 
        raise SystemExit() 
    return self.localtrace 
  
  def kill(self): 
    self.killed = True        