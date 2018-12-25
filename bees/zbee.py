import os
import zmq
import time
import redis
import random

from .utils.ip import getSelfIP
from bees.hbee import HealthBee




class ZBeeError(Exception):
    pass


class ZBee():

    '''
    bytes in bytes out.
    '''
    IP = getSelfIP()

    cpool = redis.ConnectionPool(host='localhost', port=6379,
                                 decode_responses=True, db=5)
    r = redis.Redis(connection_pool=cpool)

    def __init__(self):
        # self.ZPIPE_IN_PORT = self.pipe_receiver.bind_to_random_port(f'tcp://{self.IP}')
        # self.ZPIPE_OUT_PORT = self.ZPIPE_IN_PORT + 1
        self.ZPIPE_IN_PORT = 5557
        self.ZPIPE_OUT_PORT = 5558

        self.context = zmq.Context.instance()
        self.pipe_receiver = self.context.socket(zmq.PULL)
        self.pipe_receiver.bind(f'tcp://{self.IP}:{self.ZPIPE_IN_PORT}')
        self.semi = self.context.socket(zmq.PUSH)
        self.semi.connect(f'tcp://{self.IP}:{self.ZPIPE_OUT_PORT}')

        print(f'pipe_receiver bind to tcp://{self.IP}:{self.ZPIPE_IN_PORT}')
        print(f'semi connected to tcp://{self.IP}:{self.ZPIPE_OUT_PORT}')

        os.environ.update({'ZPIPE_IN_PORT':str(self.ZPIPE_IN_PORT)})
        os.environ.update({'ZPIPE_OUT_PORT':str(self.ZPIPE_OUT_PORT)})
        print(f'in and out ports updated into os.environ')

        self.hbee = HealthBee('zbee')
        print(f'hbee started running...')

        while True:
            time.sleep(0.1)
            print(f'pipe_receiver gonna go recv()...')
            data = self.pipe_receiver.recv()
            data = data.decode()
            if 'checkServiceStatus' in data:
                self.hbee.healthCheck()
            else:
                print(f'received from {self.ZPIPE_IN_PORT}: {data}')
                self.handle(data)

    def __del__(self):
        self.context.destroy()

    def handle(self, data) -> bool:
        data = self.unpackage(data)
        parsed = self.parse(data)
        payload = self.package(parsed)
        result = self.deliver(payload)
        print(f'payload delivered: {result}')
        return result

    def unpackage(self, data):
        if isinstance(data, bytes):
            data = data.decode()
        return data

    def parse(self, data):
        return data

    def package(self, data):

        if os.path.isfile(data):
            if data.split('.')[-1] == 'mp4':
                data = {"video": data}
            else:
                raise ZBeeError('only support mp4 now.')
        else:
            data = {"string": data}

        return data.__str__().replace("'", '"').encode()

    def deliver(self, dealt_data) -> bool:
        flag = False
        try:
            self.semi.send(dealt_data)
            print(f'sent to {self.ZPIPE_OUT_PORT}: {dealt_data}')
            flag = True
        except Exception as e:
            print(e)
            flag = False
        return flag
