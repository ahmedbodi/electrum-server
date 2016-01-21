import ast
import hashlib
from json import dumps, loads
import random
import sys
import time
import threading
import urllib
from utils import logger
from processor import Processor


class BitcoinRPC(Processor):

    def __init__(self, config, shared):
    	Processor.__init__(self)
    	self.shared = shared
	self.config = config
        self.bitcoind_url = 'http://%s:%s@%s:%s/' % (
            config.get('bitcoind', 'bitcoind_user'),
            config.get('bitcoind', 'bitcoind_password'),
            config.get('bitcoind', 'bitcoind_host'),
            config.get('bitcoind', 'bitcoind_port'))

    def wait_on_bitcoind(self):
        self.shared.pause()
        time.sleep(10)
        if self.shared.stopped():
            # this will end the thread
            raise BaseException()
            
    def call(self, method, params=[]):
        postdata = dumps({"method": method, 'params': params, 'id': 'jsonrpc'})
        while True:
            try:
                connection = urllib.urlopen(self.bitcoind_url, postdata)
                respdata = connection.read()
                connection.close()
            except:
                print_log("cannot reach bitcoind...")
                self.wait_on_bitcoind()
            else:
                r = loads(respdata)
                if r['error'] is not None:
                    if r['error'].get('code') == -28:
                        print_log("bitcoind still warming up...")
                        self.wait_on_bitcoind()
                        continue
                    raise BaseException(r['error'])
                break
        return r.get('result')

