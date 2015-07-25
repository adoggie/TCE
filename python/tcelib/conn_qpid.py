#--coding:utf-8--


"""
module: conn_qpid.py
brief:
author: scott
date:
revision:

"""

import gevent
import gevent.socket
from tce import *
from conn_mq import *
import gevent.event
from conn import RpcConnection
from endpoint import RpcEndPoint
from log import *
from message import *

class RpcConnectionQpidMQ(RpcConnection):
	def __init__(self,ep=None):
		RpcConnection.__init__(self,ep=ep)
		self.conn = None
		self.exitflag = False
		ep.impl = self
		self.mq_recv =''
		RpcConnectionMQ_Collection.instance().add(self)

	@staticmethod
	def create(name,host,port,address,af=AF_WRITE):
		"""
		创建MQ的连接对象
		:param name: 必须是真实的 mq 名称
		:param host:
		:param port:
		:param address:
		:param af:
		:return:
		"""
		ep = RpcEndPoint(name=name,host=host,port=port,addr=address,type_='qpid')
		if ep.open(af):
			return ep.impl
		return None
		# conn = RpcConnectionQpidMQ(ep)
		# conn.open(af)
		# return conn

	# @staticmethod
	# def createRpcInvocationPair(ep_read,ep_write):
	# 	conn_read = RpcConnectionQpidMQ(ep_read)
	# 	conn_read.open(AF_READ)
	# 	conn_write = RpcConnectionQpidMQ(ep_write)
	# 	conn_write.open(AF_WRITE)
	# 	conn_write.setLoopbackMQ(conn_read)
	# 	return conn_read,conn_write

	def open(self,af):
		'''
			<ep name="mq_gwa_2" address="mq_gwa_2;{create:always,node:{type:queue,durable:true}}" type="mq" host="127.0.0.1" port="5672"/>
			<ep name="mq_gwa_broadcast" address="mq_gwa_broadcast;{create:always,node:{type:topic,durable:true}}" type="mq" host="127.0.0.1" port="5672"/>
		'''
		from qpid.messaging import Connection
		from qpid.util import URL

		ep = self.ep
		self.af = af
		self.exitflag = False

		broker = "%s:%s"%(ep.host,ep.port)
		# log_debug('prepare mq : <%s %s>!'% (ep.name,broker))
		try:
			self.conn = Connection( broker,reconnect= True,tcp_nodelay=True)
			self.conn.open()
			self.ssn = self.conn.session()

			if af & AF_READ:
				self.rcv = self.ssn.receiver(self.ep.addr)
				self.rcv.capacity = 4000

				# self.thread = threading.Thread(target =self.thread_recv)
				# self.thread.start()
				# import gevent
				gevent.spawn(self.thread_recv)

			if af & AF_WRITE:
				self.snd = self.ssn.sender(self.ep.addr)

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

	def setLoopbackMQ(self,conn_recv):
		'''
			设置rpc调用的回路连接, mq_recv为回路mq的名称, mq在EasyMQ_Collection中被缓存
			目前的回路mq名称取 队列名称，如果携带主机信息的话，回路可以从另外一台mq-server返回
		'''
		self.mq_recv = conn_recv.ep.getUnique()
		return self

	def sendMessage(self,m):


		if m.traits and  m.traits.max_linger_time:
			value = m.extra.props.get(RpcMessageTraits.MAX_MSG_LINGER_TIME,'0')
			value = int(value)
			if not value:
				value +=  int(time.time())
				m.extra.setPropertyValue(RpcMessageTraits.MAX_MSG_LINGER_TIME, value )

			#app制定了超时接收时间，这里调整为绝对时间，以便接收端进行判别，选择接受还是丢弃

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

		if self.mq_recv:
			m.extra.props['__mq_return__'] = self.mq_recv
		return RpcConnection.sendMessage(self,m)

	def sendDetail(self,m):
		from qpid.messaging import Message
		try:
			if self.exitflag:
				return True
#			if not self.conn:
#				broker = "%s:%s"%(self.ep.host,self.ep.port)
#				self.conn = Connection( broker,reconnect= True,tcp_nodelay=True)
#				self.conn.open()
#				self.ssn = self.conn.session()
#				self.snd = self.ssn.sender(self.ep.addr)
			d = m.marshall()
			m = Message(d)
			self.snd.send(m,False)
		except:
			log_error(traceback.format_exc())
			# self.conn = None
			return False
		return True

	#接收消息
	def thread_recv(self):
		from communicator import RpcCommunicator
		# print 'qpid-mq recv thread start..'
		while not self.exitflag:
			try:
#				if not self.conn:
#					print 'try open mq:',self.ep.name
#					broker = "%s:%s"%(self.ep.host,self.ep.port)
#					self.conn = Connection( broker,reconnect= True,tcp_nodelay=True)
#					self.conn.open()
#					self.ssn = self.conn.session()
#					self.rcv = self.ssn.receiver(self.ep.addr)
#					self.rcv.capacity = 4000
				m = self.rcv.fetch()
				# print '.'*10
				d = m.content
				# print 'mq recv:',repr(d)
				print 'recved 1 msg from MQ..'
				self.ssn.acknowledge(sync=False)
				m = RpcMessage.unmarshall(d)
				if not m:
					log_error('decode mq-msg error!')
					continue
				m.conn = self

				value = m.extra.props.get(RpcMessageTraits.MAX_MSG_LINGER_TIME,'0')
				linger_time = int(value)
				if linger_time and time.time() > linger_time:
					# drop it
					continue	#过期接收的消息直接丢弃


				# self.dispatchMsg(m)
				RpcCommunicator.instance().dispatchMsg(m)
			except:
				log_error(traceback.format_exc())
				gevent.sleep(1)

		if self.adapter:
			self.adapter.stopmtx.set()
		# log_info("qpid-mq thread exiting..")
		return False

