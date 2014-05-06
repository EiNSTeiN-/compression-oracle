""" Sample server vulnerable to a compression oracle attack.

This is the most basic case, where a secret is compressed together 
with user data, and the compressed length is leaked somehow.
"""

import SocketServer
import zlib
import struct
import random
import string
from common import send_blob, recv_blob

secret = ''.join([random.choice(string.printable) for c in range(20)])

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = recv_blob(self.request)
        msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
        self.request.send(struct.pack('<I', len(msg)))
        return

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 30001

    print('THE SECRET IS %s' % repr(secret))

    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
