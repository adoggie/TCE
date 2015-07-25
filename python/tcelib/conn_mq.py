#--coding:utf-8--


'''
 socket通信方式的实现
 包括: connection , adapter,mqset
'''

from tce import *
from adapter import *

class RpcAdapterMQ(RpcCommAdapter):
	def __init__(self,id_,ep):
		RpcCommAdapter.__init__(self,id_,ep)
		self.addConnection(ep.impl)		# memory leak risk!!
		ep.impl.attachAdapter(self)
		ep.impl = self      #


	@staticmethod
	def create(id_,conn,*args):
		"""
			id - adapter name
			conn - (RpcConnection/ep_name)
				(endpoint name 必须已经被创建)

		"""
		from communicator import RpcCommunicator
		if isinstance(conn,str):
			conn = RpcConnectionMQ_Collection.instance().get(conn)
		adapter = RpcAdapterMQ(id_,conn.ep)
		# adapter.start()
		for conn in args:
			if isinstance(conn,str):
				conn = RpcConnectionMQ_Collection.instance().get(conn)
			adapter.addConnection( conn )
		return adapter

	def start(self):
		print 'qpid-mq:<%s> adapter started!'%self.id

	def stop(self):
		self.ep.impl.close()        #关闭mq connection

	def sendMessage(self,m):
		if self.conns:
			c = self.conns[0]
			c.sendMessage(m)
			print 'one msg sent through mq!'




class RpcConnectionMQ_Collection:
	"""
	function:  collection 为了缓存系统运行过程中创建的connection对象，防止垃圾收集器自动回收掉这些对象
	"""
	def __init__(self):
		self.list = {}

	_handle = None
	@classmethod
	def instance(cls):
		if not cls._handle:
			cls._handle = cls()
		return cls._handle

	def add(self,conn):
		self.list[conn.ep.getUnique()] = conn
		# print 'add in collection:',conn.ep.getUnique()

	def remove(self,conn):
		pass

	def get(self,name):
		return self.list.get(name)


RpcConnectionEasyMQ_Collection = RpcConnectionMQ_Collection
