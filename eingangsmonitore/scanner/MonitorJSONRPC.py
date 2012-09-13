
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from SocketServer import ThreadingMixIn
from datetime import datetime

class PresenceMonitor(object):
    """interface functions for the jsonrpc


    Provide functions login and logout with parameter uid and *args each

    Handle by putting (method, uid, date, args) tuple into provided queue
    """
    def __init__(self, queue):
        self._q = queue
     
    def login(self, uid, reminder, *args):
        """announce that the user uid has just logged in"""
        date = datetime.now()
        return self._q.put( ('login', uid, reminder, date, args) )
    def logout(self, uid, reminder, *args):
        """announce that the user uid has just logged out"""
        date = datetime.now()
        return self._q.put( ('logout', uid, reminder, date, args) )
    def message(self, msg, reminder, *args):
        """announce that the user uid has just logged out"""
        date = datetime.now()
        return self._q.put( ('message', msg, reminder, date, args) )
    def _dispatch(self, method, params):
        if method not in ('login', 'logout', 'message'):
            raise NotImplementedError()
        try:
            res = getattr(self, method)(*params)
            return "Ok"
        except:
            raise

class ThreadedJSONRPCServer(ThreadingMixIn, SimpleJSONRPCServer):
    pass

def createPresenceMonitorServer(monitor,iface, port, cls=SimpleJSONRPCServer):
    """
    Prepare the SimpleServer instance on iface:port and prep it with our 
    PresenceMonitor
    """
    server = cls( (iface, port) )
    server.register_instance(monitor)
    return server

def forkServer(iface="0.0.0.0", port=9090):
    """run Server in separate process and prepare communications via Queue
    return (Process, Queue)
    """
    from multiprocessing import Process, Queue
    _thequeue = Queue()
    monitor = PresenceMonitor(_thequeue)
    server = createPresenceMonitorServer(monitor, iface, port)
    p = Process(target = server.serve_forever, args=[])
    p.daemon = True
    p.start()
    return (p, _thequeue)

