import zmq
import sys
import threading
import time
from random import randint

__author__ = "Felipe Cruz <felipecruz@loogica.net>"
__license__ = "MIT/X11"
N_WORKERS = 10
N_CLIENTS = 1


def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'client-%d' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect('tcp://localhost:5570')
        print('Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        reqs = 0
        n_requests = 10
        while True:
            reqs = reqs + 1
            print('Req #%d sent..' % (reqs))
            for j in range(n_requests):
                socket.send_string(u'request #%d-%d' % (reqs, j))
            for i in range(N_WORKERS):
                sockets = dict(poll.poll(10))
                print(sockets)
                if socket in sockets:
                    msg = socket.recv()
                    tprint('Client %s received: %s' % (identity, msg))
                    break

        socket.close()
        context.term()


class ServerTask(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:5570')

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        workers = []
        for i in range(N_WORKERS):
            worker = ServerWorker(context)
            worker.start()
            workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()


class ServerWorker(threading.Thread):
    """ServerWorker"""
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        tprint('Worker started')
        while True:
            ident, msg = worker.recv_multipart()
            tprint('Worker received %s from %s' % (msg, ident))
            time.sleep(0.1)
            worker.send_multipart([ident, msg])

        worker.close()


def main():
    """main function"""
    server = ServerTask()
    server.start()
    for i in range(N_CLIENTS):
        client = ClientTask(i)
        client.start()

    server.join()


if __name__ == "__main__":
    main()