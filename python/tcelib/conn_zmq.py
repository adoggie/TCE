#--coding:utf-8--


"""
module: conn_q.py
brief:
	rpc shout on zmq
author: scott
date: 2015.5.10
revision:

"""


import gevent
from tce import *
from conn_mq import RpcConnectionMQ_Collection,RpcAdapterMQ
import gevent.event
from gevent_zeromq import zmq

from log import *
from conn import RpcConnection
from endpoint import RpcEndPoint
from message import *

class RpcConnectionZeroMQ(RpcConnection):
	"""
	zmq模式需broker支持
	"""
	def __init__(self,ep=None):
		import string

		RpcConnection.__init__(self,ep=ep)
		self.conn = None
		self.exitflag = False
		if ep :
			ep.impl = self
		self.mq_recv =''

		#parsing endpoint tuple
		fields = ep.addr.split(':')
		self.queue_type = fields.pop().strip().lower()
		uri = string.join(fields,':')
		self.address_read,self.address_write = map(string.strip,uri.split('%'))

		self.sock = None
		self.af = AF_NONE

		RpcConnectionMQ_Collection.instance().add(self)

	@classmethod
	def create(cls,name,address,af=AF_WRITE,host=None,port=None):
		ep = RpcEndPoint(name=name,host=host,port=port,addr=address,type='zmq')
		conn = cls(ep)
		conn.open(af)
		return conn

	def open(self,af):
		"""
		AF_WRITE - PUSH/PUB
		AF_READ - PULL/SUB
		:param af:
		:return:
		"""

		ep = self.ep
		self.af = af
		self.exitflag = False
		try:
			ctx = zmq.Context.instance()

			if af & AF_READ:
				if self.pattern == 'topic':
					self.sock = ctx.socket(zmq.SUB)
					self.sock.set(zmq.SUBSCRIBE,'')
				else: # queue
					self.sock = ctx.socket(zmq.PULL)
				self.sock.connect( self.address_read)
				gevent.spawn(self.thread_recv)

			if af & AF_WRITE:
				if self.pattern == 'topic':
					self.sock = ctx.socket(zmq.PUB)
				else: # queue
					self.sock = ctx.socket(zmq.PUSH)
				self.sock.connect( self.address_write )
		except:
			log_error(traceback.format_exc())
			return False
		# log_debug('prepare mq : <%s %s> okay!'% (ep.name,broker))
		return True

	def close(self):
		if self.conn:
			self.conn.close()
			self.conn = None
			self.exitflag = True

	def setLoopbackMQ(self,conn):
		'''
			设置rpc调用的回路连接, mq_recv为回路mq的名称, mq在EasyMQ_Collection中被缓存
			目前的回路mq名称取 队列名称，如果携带主机信息的话，回路可以从另外一台mq-server返回
		'''
		self.mq_recv = conn.ep.getUnique()
		return self

	def sendMessage(self,m):
		if m.calltype & RpcMessage.RETURN:
			#--- Rpc的调用消息中包含接收消息的队列名称 ---
			mqname = m.callmsg.extra.props.get('__mq_return__')
			if mqname:
				mq = RpcConnectionMQ_Collection.instance().get(mqname)
				if mq:
					mq.sendDetail(m)
					return
			log_error('__mq_return__:<%s> is not in service mq-list!'%mqname)
			return False

		#设置接收消息的队列名称
		if self.mq_recv:
			m.extra.props['__mq_return__'] = self.mq_recv
		return RpcConnection.sendMessage(self,m)

	def sendDetail(self,m):
		try:
			if self.exitflag:
				return True
			d = m.marshall()
			self.sock.send(d)
		except:
			log_error(traceback.format_exc())
			return False
		return True

	#接收消息
	def thread_recv(self):
		# print 'qpid-mq recv thread start..'
		while not self.exitflag:
			try:
				d = self.sock.recv()
				m = RpcMessage.unmarshall(d)
				if not m:
					log_error('decode mq-msg error!')
					continue
				m.conn = self
				# self.dispatchMsg(m)
				RpcCommunicator.instance().dispatchMsg(m)
			except:
				log_error(traceback.format_exc())
				gevent.sleep(1)

		if self.adapter:
			self.adapter.stopmtx.set()
		# log_info("qpid-mq thread exiting..")
		return False

