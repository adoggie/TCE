__author__ = 'scott'


import zmq,time

ctx = zmq.Context()
sock = ctx.socket(zmq.PUSH)
sock.connect('tcp://localhost:5566')
for n in range(100):
	sock.send('sending %s '%(n+1))
	# print sock.recv()
	time.sleep(2)
	print n

