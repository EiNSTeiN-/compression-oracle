import SocketServer
import zlib
import os
import struct

secret = "aS45Jhoap1%7xCbgsz*31A"

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client

        data = self.request.recv(4)
        #print repr(data)
        length, = struct.unpack('<I', data)
        data = ''
        while len(data) < length:
            newdata = self.request.recv(length-len(data))
            if newdata == '':
            	return
            data += newdata
        print repr(data)
        msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
        self.request.send(struct.pack('<I', len(msg)))

        return

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 30001

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()