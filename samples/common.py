import struct

def send_blob(s, data):
  s.sendall(struct.pack('<I', len(data)))
  s.sendall(data)
  return

def recv_blob(s):
  data = s.recv(4)
  length, = struct.unpack('<I', data)

  data = ''
  while len(data) < length:
    newdata = s.recv(length - len(data))
    if newdata == '':
      raise Exception('connection closed?')
    data += newdata

  return data
