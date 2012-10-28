import threading, jsonrpclib
from time import sleep


class cbeamThread ( threading.Thread ):

    def __init__(self, cbeamurl):
        threading.Thread.__init__(self) 
        self.cbeam = jsonrpclib.Server(cbeamurl)
        self.cbeamdata = {}

    def run (self):
        while True:
            tmp = self.cbeam.who()
            events = self.cbeam.events()
            tmp['events'] = events
            self.cbeamdata = tmp
            print self.cbeamdata
            sleep(10)
    def getcbeamdata(self):
        print self.cbeamdata
        return self.cbeamdata

#MyThread('http://10.0.1.27:4254').start()


