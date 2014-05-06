import socket
import struct
import string
from common import send_blob, recv_blob

from compression_oracle import CompressionOracle

HOST = '127.0.0.1'    # The remote host
PORT = 30001          # The same port as used by the server

class Client(CompressionOracle):

	def __init__(self, seed):
		CompressionOracle.__init__(self, seed=seed, 
			alphabet=string.printable, max_threads=3, 
			lookaheads=0, retries=2)
		self.s = None
		return

	def prepare_complement(self):
		return '\x00\xFF'*50

	def oracle(self, data):
		""" send 'data' to the oracle and retreived the compressed length """

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))

		s.sendall(struct.pack('<I', len(data))+data)
		data = s.recv(4)
		size, = struct.unpack('<I', data)

		s.close()
		return size

	def cleanup(self):
		return

c = Client(seed='secret=')
c.run()
