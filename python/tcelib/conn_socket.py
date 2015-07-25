#--coding:utf-8--


'''
 socket通信方式的实现
	logs:
		2014.6.19  scott  ssl supported , both server and client
			客户端ssl连接时，请求服务器地址可以是 (host,port),也可以是字符串描述: ssl://host:port

	AdapterSocket 在socket连接建立时判断是否进行user_id检查，如果没有鉴权，则AdapterSocket自动为此connection
	 生成一个序号，并在后续转发包的时候，将此序号夹带进调用的extra对象,属性: __user_id__
'''

import gevent
import gevent.socket
from 	gevent.server import StreamServer
import 	gevent.event
import gevent.ssl

# from message import *
# from tce import *
from conn import *
from endpoint import *
from adapter import *
from communicator import RpcCommunicator

class RpcConnectionSocket(RpcConnection):
	def __init__(self,adapter=None,ep=None,sock=None):
		RpcConnection.__init__(self,adapter,ep)
		self.adapter = adapter
		self.queue = NetPacketQueue()
		self.sock = sock
		self.address = None
		# self.open(ep)
		# self.mtx =gevent Semaphore()

	def getAddress(self):
		return 'RpcConnectionSocket:'+str(self.sock.getsockname())

	def open(self,af = AF_READ|AF_WRITE): #address=None,af=None):
		"""
			ep maybe :  (192.268.2.1,80)
					or instance of RpcEndPoint
		"""
		# ep = self.ep
		# if isinstance(ep,tuple) or isinstance(ep,list):
		# 	self.ep = RpcEndPoint(host=ep[0],port=ep[1])
		# else:
		# 	self.ep = ep
		# if self.ep:
		# 	self.address = (self.ep.host,self.ep.port)
		# else:
		# 	self.address = address
		# if not self.address:
		# 	return False
		return True



	def close(self):
		if self.sock:
			self.sock.close()
		# self.sock = None
		return self

	def sendMessage(self,m):
		return RpcConnection.sendMessage(self,m)

	def sendDetail(self,m):
		try:
			#self.mtx.acquire()
			if not self.sock:# and  not self.adapter:
				# import urlparse
				dest = (self.ep.host,self.ep.port)
				# scheme='tcp'
				# if isinstance(self.address,str):
				# 	cps = urlparse.urlparse(self.address)
				# 	scheme = cps.scheme.lower()
				# 	host,port = cps.netloc.split(':')
				# 	dest = (host,int(port))

				self.sock = gevent.socket.create_connection(dest,)
				# if scheme =='ssl':
				if self.ep.ssl:
					import ssl
					self.sock = gevent.ssl.wrap_socket(self.sock,)

				gevent.spawn(self.recv)
				#send token when connect on
				if self.token:
					m.extra.setPropertyValue('__token__',self.token)
				# 2014.7.1 scott
				device_id = RpcCommunicator.instance().getProperties().get('device_id')
				if device_id:
					m.extra.setPropertyValue('__device_id__',device_id)

			d = NetMetaPacket(msg=m).marshall(compress=self.getCompressionType())
			# print 'sendDetail socket',self.sock,repr(d)
			self.sock.sendall(d)
			return True
		except:
			log_error(traceback.format_exc())
			if self.sock:
				self.sock.close()
			self.sock = None
			return False
		finally:
			#self.mtx.release()
			pass

	def recv(self):
#		f = self.sock.makefile()
#		print 'socket made..'
		listener = RpcCommunicator.instance().getConnectionEventListener()
		#print 'on connected:',listener
		if listener:
			listener.onConnected(self)

		while True:
			try:
				d = self.sock.recv(1000)
				# print 'socket recved:',repr(d)
				if not d:
					break
				self.onDataRecved(d)
			except:
				# traceback.print_exc()
				break
		print 'socket lost!'
		self.sock = None
		if self.cb_disconnect:
			self.cb_disconnect(self)
		if listener:
			listener.onDisconnected(self)


	def onDataRecved(self,d):
		r = False
		r,err = self.queue.dataQueueIn(d)
		if not r:
			print r,err ,'close socket..'
			self.close() #数据解码错误，直接关闭连接
			return False
		msglist=[]
		msglist = self.queue.getMessageList()
		if len(msglist) == 0:
			return True

		for d in msglist:
			m = RpcMessage.unmarshall(d)
			if not m:
				log_error('decode mq-msg error!')
				continue


			m.conn = self
			m.user_id = self.userid

			#-- begin 2013.11.25 ---
			#当接收到第一个pkg时，判别__token__是否携带
			self.recvpkg_num += 1 # 2013.11.25
			listener = RpcCommunicator.instance().getConnectionEventListener()
			if listener:
				r = listener.onDataPacket(self,m)
				if not r: # message item ignored
					print 'eventListener filtered one message..'
					self.close()
					return
			#--- end 2013.11.25 ---
			#print m.extra.props
			# self.dispatchMsg(m)
			RpcCommunicator.instance().dispatchMsg(m)

class RpcAdapterSocket(RpcCommAdapter):
	def __init__(self,id_,ep):
		RpcCommAdapter.__init__(self,id_,ep)
		self.server = None
		ep.impl = self
		self.stopmtx = gevent.event.Event()


	def start(self):
		if self.ep.ssl:
			self.server = StreamServer((self.ep.host,self.ep.port), self._service,keyfile=self.ep.keyfile,
				certfile=self.ep.certfile)
		else:
			self.server = StreamServer((self.ep.host,self.ep.port), self._service)
#		self.server.start()
		print 'socket server started!'
		self.server.start() #serve_forever()


	def stop(self):
		self.server.stop()
		RpcCommAdapter.stop()

	def _service(self,sock,address):
		#print ' new client socket come in :',str(address)
		conn = RpcConnectionSocket(self,self.ep,sock)
		self.addConnection(conn)

		server = RpcCommunicator.instance().currentServer()
		if server.getPropertyValue('userid_check','false') == 'false':
			conn.setUserId( str(self.generateSeq()) )
			# print 'setUserid:',conn.userid
		conn.recv()
		self.removeConnection(conn)

	def sendMessage(self,m):
		RpcCommAdapter.sendMessage(self,m)
