__author__ = 'scott'


import zmq,time

ctx = zmq.Context()
sock = ctx.socket(zmq.PULL)

sock.connect('tcp://localhost:5567')

while True:
	print sock.recv()
	# sock.send("back")

