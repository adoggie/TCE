#coding:utf-8
__author__ = 'scott'

import message
from log import *

#ep types
SOCKET = 0
MQ = 1
EASYMQ= 2
QPIDMQ= 3
USER = 4
AUTO = 5
WEBSOCKET = 6
ZMQ = 7

EP_NAMES = {
		MQ: 'mq',
		SOCKET:'socket',
		EASYMQ:'easymq',
		QPIDMQ: 'qpid',
		WEBSOCKET:'websocket',
		ZMQ: 'zmq'
}


class RpcEndPoint:
	"""
	不同通信端点实现的包装类
	"""

	def __init__(self,name='',host='',port='',addr='',impl=None,keyfile='',certfile='',
		compress = 1 ,ssl=False,type_='socket',id_=0,): #message.COMPRESS_ZLIB
		self.id = id_
		self.name = name
		self.host = host
		self.port = port
		self.addr = addr.strip()
		self.user = ''
		self.passwd=''
		self.impl = impl    #具体通信方式不同实现
		self.type = type_ # in (mq,socket,websocket)
		self.keyfile = keyfile
		self.certfile = certfile
		self.compress = compress
		self.ssl = ssl 		#是否启用ssl


	def open(self,af ):
		if self.type in ('mq','easymq'):       # mesage queue , as qpid
			from conn_easymq import RpcConnectionEasyMQ
			self.impl = RpcConnectionEasyMQ(self)
		elif self.type == EP_NAMES[QPIDMQ]:
			from conn_qpid import RpcConnectionQpidMQ
			self.impl = RpcConnectionQpidMQ(self)
		elif self.type == EP_NAMES[SOCKET]:
			from conn_socket import RpcConnectionSocket
			self.impl = RpcConnectionSocket(ep=self)
		elif self.type ==EP_NAMES[WEBSOCKET]:
			from conn_websocket import RpcConnectionWebSocket
			self.impl = RpcConnectionWebSocket(ep=self)
		else:
			log_error('just support MQ type! error ep:%s %s %s'%(self.name,self.addr,self.type))
			return False
#		print str(self)
		#socket/websocket时，此刻的connection其实是个伪连接，只是保存endpoint之用，真实的操作在socketAdapter的start()
		#如果是消息队列连接，则即刻打开读/写连接
		if self.type in (EP_NAMES[MQ],EP_NAMES[EASYMQ],EP_NAMES[QPIDMQ],EP_NAMES[ZMQ]):
			return self.impl.open(af=af)
		return True


	def __str__(self):
		return 'ep: id=%s,name=%s,host=%s,port=%s,addr=%s,type=%s'%(self.id,self.name,self.host,self.port,self.addr,
		                                                            self.type)
	def close(self):
		return self.impl.close()
		pass

	def sendMessage(self,m):
#		print 'sendMessage impl:',self.impl
		if not self.impl:
			print 'no impl dispatch!'
			print str(self)
			return
		return self.impl.sendMessage(m)

	def getUnique(self):
		return self.name.strip()

	def __getUnique(self):
		import base64,hashlib
		uid = '%s:%s %s'%(self.host,self.port,self.addr)
		m = hashlib.md5()
		m.update(uid.encode('utf-8'))
		uid = base64.encodestring(m.digest()).strip()
		return uid

	@property
	def uniqueName(self):
		return self.getUnique()