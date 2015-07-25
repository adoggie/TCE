#--coding:utf-8--


'''
 websocket通信方式的实现
'''


from message import *
from tce import *
from adapter import *
from conn import *

class RpcConnectionWebSocket(RpcConnection):
	def __init__(self,adapter=None,ep=None,sock=None):
		RpcConnection.__init__(self,adapter,ep)
		self.adapter = adapter
		self.queue = NetPacketQueue()
		self.sock = sock
		self.address = None

	def open(self,address=None,af=None):
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
#			if not self.sock:
#				self.sock = gevent.socket.create_connection(self.address,)
#				gevent.spawn(self.recv)
			# d = NetMetaPacket(msg=m).marshall(compress=self.getCompressionType())
			d = NetMetaPacket(msg=m).marshall(compress=message.COMPRESS_NONE)
			#			print 'sendDetail socket',self.sock,repr(d)
			d = bytearray(d)
#			print d
			self.sock.send(d)
		except:
			log_error(traceback.format_exc())
			if self.sock:
				self.sock.close()
			self.sock = None
			return False
		return True

#	def recv(self):
#	#		f = self.sock.makefile()
#		while True:
#			try:
#			#				print 'ready socket redv..'
#			#				d = f.read(1024*10)
#				d = self.sock.recv(1000)
#				#				print 'connection recv:',repr(d)
#				if not d:
#					break
#				self.onDataRecved(d)
#			except:
#				traceback.print_exc()
#				break
#		print 'socket lost!'
#		self.sock = None


	def onDataRecved(self,d):
		from communicator import RpcCommunicator
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
			# RpcCommunicator.instance().dispatchMsg(m)
			m.user_id = self.userid
			# self.dispatchMsg(m)

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


	def recv(self):
		from communicator import  RpcCommunicator
		listener = RpcCommunicator.instance().getConnectionEventListener()
		if listener:
			listener.onConnected(self)

		while True:
			try:
				d = self.sock.receive()
				if not d:
					break
				self.onDataRecved( str(d) )
			except:
				# traceback.print_exc()
				break
		print 'websocket lost!'
		self.sock = None
		if self.cb_disconnect:
			self.cb_disconnect(self)
		if listener:
			listener.onDisconnected(self)


class RpcAdapterWebSocket(RpcCommAdapter):
	def __init__(self,id,ep):
		RpcCommAdapter.__init__(self,id,ep)
		self.server = None
		ep.impl = self

	def start(self):
		from gevent.pywsgi import WSGIServer
		import geventwebsocket
		from geventwebsocket.handler import WebSocketHandler

		# geventwebsocket.WebSocketServer
		# self.server = WSGIServer((self.ep.host,self.ep.port), self._service, handler_class=geventwebsocket.WebSocketHandler)

		if self.ep.ssl:
			self.server = WSGIServer((self.ep.host,self.ep.port), self._service, handler_class=WebSocketHandler,keyfile=self.ep.keyfile,certfile=self.ep.certfile)
		else:
			self.server = WSGIServer((self.ep.host,self.ep.port), self._service, handler_class=WebSocketHandler)
		print 'websocket server started!'
		self.server.start() #.serve_forever()

	def stop(self):
		self.server.stop()
		self.stopmtx.set()


	def _http_handler(environ, start_response):
		import geventwebsocket
		if environ["PATH_INFO"].strip("/") == "version":
			start_response("200 OK", [])
			agent = "gevent-websocket/%s" % (geventwebsocket.get_version())
			return [agent]
		else:
			start_response("400 Bad Request", [])
		return ["WebSocket connection is expected here."]

	def _service(self,environ, start_response):
		from communicator import RpcCommunicator
		print ' new client websocket come in :'#,str(address)
		sock = environ.get("wsgi.websocket")
		if sock is None:
			return self._http_handler(environ, start_response)
		conn = RpcConnectionWebSocket(self,self.ep,sock)
		self.addConnection(conn)

		server = RpcCommunicator.instance().currentServer()
		if server.getPropertyValue('userid_check','false') == 'false':
			conn.setUserId( str(self.generateSeq()) )
		conn.recv()

		self.removeConnection(conn)


	def sendMessage(self,m):
		RpcCommAdapter.sendMessage(self,m)

if __name__=='__main__':
	pass