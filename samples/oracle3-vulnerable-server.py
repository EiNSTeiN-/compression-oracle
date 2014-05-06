""" Sample server vulnerable to a compression oracle attack.

This is an example of some data being compressed and the 
compressed stream being transmitted with a measurable delay.
This delay can be caused by many things, like for example the 
delay introduced by waiting for a TCP ACK after too many 
packets are transmitted.

In this example we introduce a random artificial delay for each 
chunk of 300 bytes. Only the response 'ok' is returned, so that 
the only observable side-channel is the wait time.
"""

import SocketServer
import zlib
import random
import string
import time
from common import send_blob, recv_blob

secret = ''.join([random.choice(string.printable) for c in range(20)])

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = recv_blob(self.request)
        msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
        t = sum([random.randint(600,700) / 1000. for i in range(len(msg) / 300)])
        time.sleep(t)
        send_blob(self.request, 'ok')
        return

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 30001

    print('THE SECRET IS %s' % repr(secret))

    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
