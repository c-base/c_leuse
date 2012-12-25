import threading, jsonrpclib
from jsonrpc.proxy import ServiceProxy
from time import sleep


class cbeamThread ( threading.Thread ):

    def __init__(self, cbeamurl):
        threading.Thread.__init__(self) 
        self.cbeam = ServiceProxy(cbeamurl)
        self.cbeamdata = {}

    def run (self):
        while True:
            tmp = self.cbeam.who()['result']
            events = self.cbeam.events()['result']
            tmp['events'] = events
            self.cbeamdata = tmp
            sleep(10)
            print "c-beam data updated."
    def getcbeamdata(self):
        print self.cbeamdata
        return self.cbeamdata

#MyThread('http://10.0.1.27:4254').start()


