#--coding:utf-8--


'''
 socket通信方式的实现
 包括: connection , adapter,mqset
'''

import gevent
import gevent.socket
import gevent.event

from gevent import monkey
from tce import *
from conn_mq import *
from endpoint import RpcEndPoint
from conn import RpcConnection


class RpcConnectionEasyMQ(RpcConnection):
	def __init__(self,ep):
		RpcConnection.__init__(self,ep=ep)
		self.conn = None
		self.exitflag = False
		ep.impl = self
		self.mq_recv='' #RPC调用返回消息回送的mq名称
		RpcConnectionEasyMQ_Collection.instance().add(self)

	@staticmethod
	def create(name,host,port,address,af=AF_WRITE):
		ep = RpcEndPoint(name=name,host=host,port=port,addr=address,type='easymq')
		conn = RpcConnectionEasyMQ(ep)
		conn.open(af)
		return conn

	def open(self,af):
		import easymq

		ep = self.ep
		self.af = af
		self.exitflag = False
		# ep.addr - 'topic/queue:ctrlserver-1'
		mqtype,name = ep.addr.split(':')
		if mqtype.lower().strip() == 'topic':
			mqtype = easymq.TOPIC
		else:
			mqtype = easymq.QUEUE
		name = name.strip().lower()

		#log_debug('prepare mq : <%s %s:%s address:%s>!'% (ep.name,ep.host,ep.port,ep.addr))

		if af & AF_READ:
			self.conn = easymq.Connection((ep.host,ep.port),name,mqtype,mode=easymq.READ)
		else:
			self.conn = easymq.Connection((ep.host,ep.port),name,mqtype,mode=easymq.WRITE)
		self.conn.open()
		if af & AF_READ:
			gevent.spawn(self.thread_recv)
		#print 'conn open:',self.ep.name

		# log_debug('prepare mq : <%s %s> okay!'% (ep.name,ep.addr))
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
		if m.calltype & RpcMessage.RETURN: #处理转发回送数据 包
			#--- 处理直接操作mq进行rpc调用的情形 ---
			mqname = m.callmsg.extra.props.get('__mq_return__')
			if mqname:
				mq = RpcConnectionEasyMQ_Collection.instance().get(mqname)
				if mq:
					#del m.callmsg.extra.props['__mq_return__']
					mq.sendDetail(m)
					return
			# --- end ----
			log_error('__mq_return__:%s is not in service mq-list!'%mqname)
			return False

#			type_,id = (m.call_id>>8)&0xff, m.call_id&0xff
			type_,id = (m.call_id>>8)&0x7f, m.call_id&0xff
			#类型的最高位不用
			svc = RpcCommunicator.instance().getServiceDetail(type_)
			if not svc:
				log_error('not found service: src_type =%s'%type_)
				return False
			mqname =svc.pattern%id
#			print mqname
			ep = RpcCommunicator.instance().currentServer().findEndPointByName(mqname)
			if not ep:
				log_error('ep <%s> undefined!'%mqname)
				return False
			return  ep.impl.sendDetail(m)

#		server = RpcCommunicator.instance().currentServer()
#		if server.getPropertyValue('userid_check','false') == 'true':
#			if not self.userid: #未认证通过
#				return True
		# calltype == CALL  携带 user_id到mq接收者
		if self.mq_recv:
			m.extra.props['__mq_return__'] = self.mq_recv
		#print 'mq sendmessage ..',m
		return RpcConnection.sendMessage(self,m)

	def sendDetail(self,m):
		# from qpid.messaging import Message
		import easymq
		try:
			if self.exitflag:
				return True
			d = m.marshall()
			m = easymq.Message(d)
			self.conn.write(m)
			#print 'EasyMQ:: sendDetail ',m
		except:
			log_error(traceback.format_exc())
			# self.conn = None
			return False
		return True

	#接受消息
	def thread_recv(self):
		#print 'easy-mq recv thread start..'
		while not self.exitflag:
			try:
				m = self.conn.read()
				if not m:
					gevent.sleep()
					continue
				d = m.data
				m = RpcMessage.unmarshall(d)
				if not m:
					log_error('decode mq-msg error!')
					continue
				m.conn = self
				# self.dispatchMsg(m)
				#print 'EasyMQ:: got one msg ',m
				RpcCommunicator.instance().dispatchMsg(m)
			except:
				log_error(traceback.format_exc())
				gevent.sleep(1)
		if self.adapter:
			self.adapter.stopmtx.set()
		#log_info("mq thread exiting..")
		return False
