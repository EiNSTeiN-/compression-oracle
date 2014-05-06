""" Sample server vulnerable to a compression oracle attack.

This is an example of compressed data being encrypted using a 
block cipher, and the ciphertext length is leaked somehow.

Because of the nature of block ciphers, the compressed length
that is observable to the attacker is rounded to the nearest
multiple of the block length, 8 bytes in this case.
"""

import SocketServer
import zlib
import os
import random
import string
from common import send_blob, recv_blob
from Crypto.Cipher import DES

secret = ''.join([random.choice(string.printable) for c in range(20)])

def encrypt(data):
    iv = os.urandom(8)
    des = DES.new('01234567', DES.MODE_CBC, iv)
    data += '\x00' * (8 - len(data) % 8)
    ciphertext = iv + des.encrypt(data)
    return ciphertext

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = recv_blob(self.request)
        msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
        send_blob(self.request, encrypt(msg))
        return

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 30001

    print('THE SECRET IS %s' % repr(secret))

    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
