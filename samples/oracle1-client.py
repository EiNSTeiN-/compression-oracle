import socket
import struct
import string

from compression_oracle import CompressionOracle

HOST = '127.0.0.1'    # The remote host
PORT = 30001          # The same port as used by the server

class Client(CompressionOracle):

	def __init__(self, prefix):
		CompressionOracle.__init__(self, seed=prefix, alphabet=string.printable, max_threads=10)
		self.s = None
		return

	def prepare(self):
		return

	def oracle(self, data):
		""" send 'data' to the oracle and retreived the compressed length """

		exceptions = 0
		while exceptions < 3:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST, PORT))

				s.sendall(struct.pack('<I', len(data))+data)
				data = s.recv(4)
				size, = struct.unpack('<I', data)
				#print 'Received', repr(size)

				s.close()
				return size
			except:
				print 'exception occured'
				exceptions += 1

	def cleanup(self):
		return

c = Client(seed='secret=')
c.run()
