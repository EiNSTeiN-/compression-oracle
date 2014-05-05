import SocketServer
import zlib
import os
import struct
from common import send_blob, recv_blob

secret = "aS45Jhoap1%7xCbgsz*31A"

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client

        data = recv_blob(self.request)
        print repr(data)
        msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
        self.request.send(struct.pack('<I', len(msg)))

        return

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 30001

    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()