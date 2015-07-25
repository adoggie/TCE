#coding:utf-8
__author__ = 'scott'

"""
zmq_router.py
提供PUB/SUB，PUSH/PULL的代理broker功能



@auth: scott
@date: 2015.5.22

"""
import yaml,sys,os,time,traceback,getopt
from gevent import spawn,joinall
import zmq.green as zmq
# import zmq
# from gevent_zeromq import zmq



class Broker:
	def __init__(self,name,front_addr,back_addr,type='push'):
		self.name = name
		self.front_addr = front_addr
		self.back_addr = back_addr
		self.type = type

		self.let = None
		self.frontend = None
		self.backend = None

	def init(self):
		print 'initializing broker: %s >> %s'%(self.front_addr,self.back_addr)
		context = zmq.Context()
		if 'push' in self.type:
			self.frontend = context.socket(zmq.PULL)
			self.backend  = context.socket(zmq.PUSH)
		else:
			self.frontend = context.socket(zmq.SUB)
			self.backend  = context.socket(zmq.PUB)


		self.frontend.bind(self.front_addr)
		self.backend.bind(self.back_addr)
		self.let = spawn(self.proxy, self.frontend, self.backend)
		# self.proxy(self.frontend,self.backend)

	def proxy(self,socket_from, socket_to):
		while True:
			m = socket_from.recv_multipart()
			print 'recv_multipart:',m
			socket_to.send_multipart(m)



def read_serivce_address_pair():
	"""
	命令行拾取yml格式的broker配置文件,读取服务地址对配置信息
	brokers:
		- name: test1
		  front: tcp://*:5566
		  back: tcp://*5567

		- name: test2
		  front: tcp://*:5566
		  back: tcp://*5567
	:return:
	"""
	props = None
	brokers = []
	options,args = getopt.getopt(sys.argv[1:],"hf:",["help","file="])
	filename = './config.yml'
	for name,value in options:
		if name in ('-h','--help'):
			pass
		if name in ('-f','--file'):
			filename = value

	f = open(filename)
	props = yaml.load(f.read())
	f.close()
	for broker in props['brokers']:
		brokers.append( broker )
	return brokers


class BrokerCollection:
	brokers = []

	@staticmethod
	def joinall():
		lets = map(lambda broker:broker.let,BrokerCollection.brokers)
		joinall(lets)

def start_broker(name,front_addr,back_addr):
	broker = Broker(name,front_addr,back_addr)
	broker.init()
	return broker

def stop_broker(name):
	pass

def list_brokers():
	pass


def startup():
	brokers = []
	addresses = read_serivce_address_pair()
	print addresses
	for b in addresses:
		name,front,back = b['name'],b['front'],b['back']
		brokers.append( start_broker( name, front,back))
	BrokerCollection.brokers = brokers
	BrokerCollection.joinall()

def usage():
	print 'zmq_router.py --help | --file=broker.yml'


if __name__ == '__main__':
	"""

	"""
	startup()



# import zmq
#
# # Prepare our context and sockets
# context = zmq.Context()
# frontend = context.socket(zmq.PULL)
# backend = context.socket(zmq.PUSH)
# frontend.bind("tcp://*:5566")
# backend.bind("tcp://*:5567")
#
#
# # Switch messages between sockets
# while True:
# 	message = frontend.recv_multipart()
# 	print message
# 	backend.send_multipart(message)
