import socket
import string
from common import send_blob, recv_blob

from compression_oracle import CompressionOracle, TwoTriesBlockCipherGuess

HOST = '127.0.0.1'    # The remote host
PORT = 30001          # The same port as used by the server

class Client(CompressionOracle):

	def __init__(self, seed):
		CompressionOracle.__init__(self, seed=seed, 
			alphabet=string.printable, max_threads=3, 
			lookaheads=0, retries=2, guess_provider=TwoTriesBlockCipherGuess)
		return

	def prepare_complement(self):
		return '\x00\xFF'*50

	def oracle(self, data):
		""" send 'data' to the oracle and retreived the compressed length """

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))

		send_blob(s, data)
		data = recv_blob(s)

		s.close()
		return len(data)

	def cleanup(self):
		return

c = Client(seed='secret=')
c.run()
