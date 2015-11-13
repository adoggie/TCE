#--coding:utf-8 --
__author__ = 'scott'


import time,threading
import message
from message import  RpcMessage
from service import RpcIfRouteDetail,RpcRouteInoutPair

class RpcConnectionEventListener:
	def __init__(self):
		pass

	def onConnected(self,conn):
		pass

	def onDisconnected(self,conn):
		pass

	def onDataPacket(self,conn,msg):
		'''
			返回True进入事件分派，False则丢弃消息
		'''
		return True



class RpcConnection:
	MQ = 1
	SOCKET = 2
	def __init__(self,adapter=None,ep=None):

		self.ep = ep # RpcEndpoint
		self.conn = None
		self.delta = None
		self.rpcmsglist={}
		# self.mtxrpc = threading.Lock() #连接断开，必须让通知等待rpc调用返回的对象
		self.id = str(time.time())

		self.adapter = adapter

		self.budyconn = None #伙伴连接，读连接对应写连接
				#socket时budyconn就是自己
		self.userid = ''
		self.cb_disconnect = None
		self.id = 0

		self.recvpkg_num = 0  # 已接受报文数量
		self.token = ''
		self.appuser = None


	def destroy(self):
		self.adapter = None
		self.budyconn = None
		self.ep = None
		self.conn = None
		self.appuser = None


	def getAddress(self):
		return 'RpcConnection:'+str(id(self))

	def setToken(self,token):
		self.token = token

	def getRecvedMessageCount(self):
		return self.recvpkg_num

	#将一个服务适配器绑定到一个连接上
	#之后连接上接收到的rpc消息被传递到adapter处理
	#通常应用在 client发起连接之后，server利用此连接反向调用client的服务类
	def attachAdapter(self,adapter):
		self.adapter =  adapter

	setAdatper = attachAdapter

	def detachAdapter(self):
		if self.adapter:
			self.adapter.removeConnection(self)
			self.adapter = None



	def setUserId(self,userid):
		from log  import log_warn
		if not userid:
			 print  'warning : RpcConnection.setUserId() user_id illegal: '+ str(userid)
		# userid = str(userid)
		if self.adapter:
			self.adapter.mapConnectionWithUserId(self,userid)
		self.userid = userid

	def getUserId(self):
		return self.userid

	def connect(self):
		return False


	def doReturnMsg(self,m2):
		from communicator import  RpcCommunicator
#		print 'doReturnMsg',m2,m2.sequence,repr(m2)
		m1 = RpcCommunicator.instance().dequeueMsg(m2.sequence)
		if m1:
			if m1.async:                #异步通知
				m1.asyncparser(m1, m2)   #m2.paramstream,m2.async,m2.prx)
			else:
#				m1.mtx.notify(m2)       # 传递到等待返回结果的对象线程
				m1.mtx.set(m2)


	def dispatchMsg(self,m):
		from communicator import  RpcCommunicator
		server = RpcCommunicator.instance().currentServer()
		if m.calltype & RpcMessage.CALL:

			#rpc调用请求
			if self.adapter:
				# print 'containedIf:',self.adapter.containedIf(m.ifidx)
				if self.adapter.containedIf(m.ifidx):
					# print 'adapter.dispatchMsg',m
					self.adapter.dispatchMsg(m)
					return
			# redirect to next

			#用户未认证，不能转发到下级节点
			route = server.routes.get(m.ifidx)  #查找接口路由信息
			if route:
				if self.ep.type in ('socket','websocket'): # 内向外的rpc请求
					#-- 鉴别用户是否已经通过认证  userid=0 非法用户编号
					server = RpcCommunicator.instance().currentServer()
					if server.getPropertyValue('userid_check','false') == 'true': #判别舒服需要用户检查
						if not self.userid: #用户id为0，未认证连接，取消转发
							print 'userid checked (is null),unauthorized skip redirect..'
							return
				if self.userid:
					m.extra.props['__user_id__'] = str(self.userid)
				else:
					print 'user_id is null, __user_id__ not apply.'
				#开始查找路由表，定位
				inout = route.getRouteInoutPair(RpcIfRouteDetail.CALL,self.ep.id)
				if inout:   #路由输出ep
					peer_ep = inout.out
					# if peer_ep.type !='mq':
					# 	log_error('out-ep must be mq-type ,please check config of server: %s '%server.name)
					# 	return
					m.call_id |= 1<<15  #最高位1表示此消息包是转发消息包
					#print 'redirect CALL msg,call_id',hex(m.call_id)
					peer_ep.sendMessage(m)
					#系统开始，用于已经将rpc调用回路设置好了 EasyMqConnection.setLoopbackMq()

		if m.calltype & RpcMessage.RETURN:
			#print 'call_id:',hex(m.call_id),m.extra.props
			#最高位为0表示此RETURN为本地调用产生的RETURN
			#routes表项记录为空，表示非转发服务，直接本地处理
			if not m.call_id>>15 or not server.routes:
				self.doReturnMsg(m)
				return
			#分派到其他ep
			# type_,id = (m.call_id>>8)&0x7f, m.call_id&0xff
			route = server.routes.get(m.ifidx)
			#print 'RETURN:',route
			if route:
				inout = route.getRouteInoutPair(RpcIfRouteDetail.RETURN,self.ep.id)
				if inout:   #路由输出ep
					peer_ep = inout.out
					print 'redirect RETURN ..'
					peer_ep.sendMessage(m)


	def close(self):
		return self

	def sendMessage(self,m):
		from communicator import  RpcCommunicator
		if m.calltype&RpcMessage.CALL:
			# if not m.extra.props.get('__user_id__'):
			# 	m.extra.props['__user_id__'] = str(m.user_id)

			#2013.11.25 following line commented
#			m.call_id |= RpcCommunicator.instance().currentServer().getId()

			if m.calltype& RpcMessage.ONEWAY == 0:
				RpcCommunicator.instance().enqueueMsg(m) #置入等待队列
		r = False
		r = self.sendDetail(m)
		if not r:
			if m.calltype&RpcMessage.CALL: #发送失败，删除等待队列中的消息
				if m.calltype& RpcMessage.ONEWAY == 0:
					RpcCommunicator.instance().dequeueMsg(m.sequence)
		return r

	def sendDetail(self,m):
		return False

	def getCompressionType(self):
		'''
			获取数据压缩方式
			默认: zlib
		'''
		ep = None
		if self.adapter:
			ep = self.adapter.getEndpoint()
		else:
			ep = self.ep
		compress = message.COMPRESS_ZLIB
		if ep:
			compress = ep.compress
		return compress

