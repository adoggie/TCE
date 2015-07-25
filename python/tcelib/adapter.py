# -- coding:utf-8 --
__author__ = 'scott'

import time,traceback,threading
from tce import *
from message import *
import gevent.event

class RpcCommAdapter:
	def __init__(self,id_,ep=None):
		self.ep = ep
		self.servants = {}  # idx:servant
		self.id = id_
		self.conns =[]
		self.user_conns={}
		self.logger = None
		self.stopmtx = gevent.event.Event()
		self.sequence = 0

	def getUserConnection(self,userid):
		return self.user_conns.get(userid)

	def getEndpoint(self):
		return self.ep

	def getUserConnection(self,userid):
		return self.user_conns.get(userid)

	def getMutex(self):
		return self.stopmtx

	def makeUniqueId(self):
		return str(time.time())

	def generateSeq(self):
		self.sequence+=1
		if self.sequence >0xffffff00:
			self.sequence = 1
		return self.sequence

	def start(self):
		return True

	def stop(self):
		self.getMutex().set()

	def join(self):
		self.getMutex().wait()
#		self.stopmtx.wait() #驱动时间模型

	#目前不支持单用户id在多conn上登陆传输
	def mapConnectionWithUserId(self,conn,userid):
		self.user_conns[userid] = conn

	def addConnection(self,conn):
		conn.setAdatper(self)
		self.conns.append(conn)

	def removeConnection(self,conn):
		conn.destroy()
		if self.conns.count(conn):
			self.conns.remove(conn)

		c = self.user_conns.get(conn.userid)
		if c == conn:
			del self.user_conns[conn.userid]

	def addServant(self,servant):

		for ifidx,dgcls in servant.delegatecls.items():
			dg = dgcls(servant,self)
			dg.id = self.makeUniqueId()
			self.servants[ dg.index ] = dg
		return self


	def containedIf(self,ifidx):
#		print self.servants
		return self.servants.has_key(ifidx)

	def dispatchMsg(self,m):
		#print 'Adapter Got Msg..',str(m)
		if m.calltype & RpcMessage.CALL:
			if not self.servants.has_key(m.ifidx): #不存在调用接口类
				self._doError(RPCERROR_INTERFACE_NOTFOUND,m)
				return
			dg = self.servants[m.ifidx]
			if not dg.optlist.has_key(m.opidx): #不存在接口函数
				self._doError(RPCERROR_INTERFACE_NOTFOUND,m)
				return
			func = dg.optlist[m.opidx]

			ctx = RpcContext()
#			if not conn.delta:
#				conn.delta = RpcConnection(conn)
			ctx.conn = m.conn  # it's RpcConnection
			ctx.msg = m
			try:
				func( ctx ) #讲消息传递到 servant对象的函数 (通过elegate间接传递)
			except:
				traceback.print_exc()
				self._doError(RPCERROR_REMOTEMETHOD_EXCEPTION,m)

#		if  m.calltype & RpcMessage.RETURN: # 在同一个连接上实现 rpc 复用
#			rpc = conn.delta
#			rpc.doReturnMsg(m)

	def _doError(self,errcode,m):
		errmsg = RpcMessageReturn()
		errmsg.sequence = m.sequence
		errmsg.errcode = errcode
		m.conn.sendMessage(errmsg)

	def sendMessage(self,m):
		conn = self.user_conns.get(m.user_id)    #找到连接对象
		print self.user_conns
		if conn:
			conn.sendMessage(m)