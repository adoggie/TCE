
# -- coding:utf-8 --

#---------------------------------
#  TCE
#  Tiny Communication Engine
#
#  sw2us.com copyright @2012
#  bin.zhang@sw2us.com / qq:24509826
#---------------------------------

import os,os.path,sys,struct,time,traceback,time
import tcelib as tce

	
class BaseServer(tce.RpcServantBase):
	# -- INTERFACE -- 
	def __init__(self):
		tce.RpcServantBase.__init__(self)
		if not hasattr(self,'delegatecls'):
			self.delegatecls = {}
		self.delegatecls[0] = BaseServer_delegate
	
	def datetime(self,ctx):
		return ''
		

class BaseServer_delegate:
	def __init__(self,inst,adapter,conn=None):
		self.index = 0
		self.optlist={}
		self.id = '' 
		self.adapter = adapter
		self.optlist[0] = self.datetime
		
		self.inst = inst
	
	def datetime(self,ctx):
		tce.log_debug("callin (datetime)")
		d = ctx.msg.paramstream 
		idx = 0
		cr = None
		cr = self.inst.datetime(ctx)
		if not cr : return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		d = tce.serial_string(cr,d)
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	
class BaseServerPrx(tce.RpcProxyBase):
	# -- INTERFACE PROXY -- 
	def __init__(self,conn):
		tce.RpcProxyBase.__init__(self)
		self.conn = conn
		self.delta = None
		pass
	
	@staticmethod
	def create(ep,af= tce.AF_WRITE | tce.AF_READ):
		ep.open(af)
		conn = ep.impl
		proxy = BaseServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithEpName(name):
		ep = tce.RpcCommunicator.instance().currentServer().findEndPointByName(name)
		if not ep: return None
		conn = ep.impl
		proxy = BaseServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithProxy(prx):
		proxy = BaseServerPrx(prx.conn)
		return proxy
	
	#extra must be map<string,string>
	def datetime(self,timeout=None,extra={}):
		# function index: 0
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 0
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
		idx_6 = 0
		d_9 = m_1.paramstream
		p_7 = None
		r_8 = False
		try:
			p_7 = None
			p_7,idx_6 = tce.unserial_string(d_9,idx_6)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_UNSERIALIZE_FAILED)
		return p_7
	
	def datetime_async(self,async,cookie=None,extra={}):
		# function index: idx_6
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 0
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = BaseServerPrx.datetime_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def datetime_asyncparser(m,m2):
		# function index: idx_6 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			p_7 = None
			p_7,idx_4 = tce.unserial_string(d_5,idx_4)
			if r_6:
				user_2(p_7,prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	

class ITerminalGatewayServer(tce.RpcServantBase):
	# -- INTERFACE -- 
	def __init__(self):
		tce.RpcServantBase.__init__(self)
		if not hasattr(self,'delegatecls'):
			self.delegatecls = {}
		self.delegatecls[1] = ITerminalGatewayServer_delegate
	
	def ping(self,ctx):
		pass
	

class ITerminalGatewayServer_delegate:
	def __init__(self,inst,adapter,conn=None):
		self.index = 1
		self.optlist={}
		self.id = '' 
		self.adapter = adapter
		self.optlist[0] = self.ping
		
		self.inst = inst
	
	def ping(self,ctx):
		tce.log_debug("callin (ping)")
		d = ctx.msg.paramstream 
		idx = 0
		cr = None
		self.inst.ping(ctx)
		if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	
class ITerminalGatewayServerPrx(tce.RpcProxyBase):
	# -- INTERFACE PROXY -- 
	def __init__(self,conn):
		tce.RpcProxyBase.__init__(self)
		self.conn = conn
		self.delta = None
		pass
	
	@staticmethod
	def create(ep,af= tce.AF_WRITE | tce.AF_READ):
		ep.open(af)
		conn = ep.impl
		proxy = ITerminalGatewayServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithEpName(name):
		ep = tce.RpcCommunicator.instance().currentServer().findEndPointByName(name)
		if not ep: return None
		conn = ep.impl
		proxy = ITerminalGatewayServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithProxy(prx):
		proxy = ITerminalGatewayServerPrx(prx.conn)
		return proxy
	
	#extra must be map<string,string>
	def ping(self,timeout=None,extra={}):
		# function index: 1
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 1
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
	
	def ping_async(self,async,cookie=None,extra={}):
		# function index: 1
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 1
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ITerminalGatewayServerPrx.ping_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def ping_asyncparser(m,m2):
		# function index: 1 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			if r_6:
				user_2(prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	def ping_oneway(self,extra={}):
		# function index: idx_4
		
		try:
			m_1 = tce.RpcMessageCall(self)
			m_1.ifidx = 1
			m_1.opidx = 0
			m_1.calltype |= tce.RpcMessage.ONEWAY
			m_1.prx = self
			m_1.conn = m_1.prx.conn
			m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
			m_1.extra.setStrDict(extra)
			r_4 = self.conn.sendMessage(m_1)
			if not r_4:
				raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	

class Server(tce.RpcServantBase):
	# -- INTERFACE -- 
	def __init__(self):
		tce.RpcServantBase.__init__(self)
		if not hasattr(self,'delegatecls'):
			self.delegatecls = {}
		self.delegatecls[2] = Server_delegate
	
	def echo(self,text,ctx):
		return ''
		
	def timeout(self,secs,ctx):
		pass
	
	def heartbeat(self,hello,ctx):
		pass
	
	def bidirection(self,ctx):
		pass
	

class Server_delegate:
	def __init__(self,inst,adapter,conn=None):
		self.index = 2
		self.optlist={}
		self.id = '' 
		self.adapter = adapter
		self.optlist[0] = self.echo
		self.optlist[1] = self.timeout
		self.optlist[2] = self.heartbeat
		self.optlist[3] = self.bidirection
		
		self.inst = inst
	
	def echo(self,ctx):
		tce.log_debug("callin (echo)")
		d = ctx.msg.paramstream 
		idx = 0
		_p_text,idx = tce.unserial_string(d,idx)
		cr = None
		cr = self.inst.echo(_p_text,ctx)
		if not cr : return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		d = tce.serial_string(cr,d)
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	def timeout(self,ctx):
		tce.log_debug("callin (timeout)")
		d = ctx.msg.paramstream 
		idx = 0
		_p_secs,idx = tce.unserial_int(d,idx)
		cr = None
		self.inst.timeout(_p_secs,ctx)
		if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	def heartbeat(self,ctx):
		tce.log_debug("callin (heartbeat)")
		d = ctx.msg.paramstream 
		idx = 0
		_p_hello,idx = tce.unserial_string(d,idx)
		cr = None
		self.inst.heartbeat(_p_hello,ctx)
		if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	def bidirection(self,ctx):
		tce.log_debug("callin (bidirection)")
		d = ctx.msg.paramstream 
		idx = 0
		cr = None
		self.inst.bidirection(ctx)
		if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	
class ServerPrx(tce.RpcProxyBase):
	# -- INTERFACE PROXY -- 
	def __init__(self,conn):
		tce.RpcProxyBase.__init__(self)
		self.conn = conn
		self.delta = None
		pass
	
	@staticmethod
	def create(ep,af= tce.AF_WRITE | tce.AF_READ):
		ep.open(af)
		conn = ep.impl
		proxy = ServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithEpName(name):
		ep = tce.RpcCommunicator.instance().currentServer().findEndPointByName(name)
		if not ep: return None
		conn = ep.impl
		proxy = ServerPrx(conn)
		return proxy
	
	@staticmethod
	def createWithProxy(prx):
		proxy = ServerPrx(prx.conn)
		return proxy
	
	#extra must be map<string,string>
	def echo(self,text,timeout=None,extra={}):
		# function index: 2
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 2
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		d_2 = '' 
		d_2 = tce.serial_string(text,d_2)
		m_1.paramstream += d_2
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
		idx_6 = 0
		d_9 = m_1.paramstream
		p_7 = None
		r_8 = False
		try:
			p_7 = None
			p_7,idx_6 = tce.unserial_string(d_9,idx_6)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_UNSERIALIZE_FAILED)
		return p_7
	
	def echo_async(self,text,async,cookie=None,extra={}):
		# function index: idx_6
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 2
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		d_3 = '' 
		d_3 = tce.serial_string(text,d_3)
		m_1.paramstream += d_3
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ServerPrx.echo_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def echo_asyncparser(m,m2):
		# function index: idx_6 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			p_7 = None
			p_7,idx_4 = tce.unserial_string(d_5,idx_4)
			if r_6:
				user_2(p_7,prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	#extra must be map<string,string>
	def timeout(self,secs,timeout=None,extra={}):
		# function index: idx_4
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 2
		m_1.opidx = 1
		m_1.extra.setStrDict(extra)
		d_2 = '' 
		d_2 += tce.serial_int(secs,d_2)
		m_1.paramstream += d_2
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
	
	def timeout_async(self,secs,async,cookie=None,extra={}):
		# function index: idx_4
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 2
		m_1.opidx = 1
		m_1.extra.setStrDict(extra)
		d_3 = '' 
		d_3 += tce.serial_int(secs,d_3)
		m_1.paramstream += d_3
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ServerPrx.timeout_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def timeout_asyncparser(m,m2):
		# function index: idx_4 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			if r_6:
				user_2(prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	def timeout_oneway(self,secs,extra={}):
		# function index: idx_4
		
		try:
			m_1 = tce.RpcMessageCall(self)
			m_1.ifidx = 2
			m_1.opidx = 1
			m_1.calltype |= tce.RpcMessage.ONEWAY
			m_1.prx = self
			m_1.conn = m_1.prx.conn
			m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
			m_1.extra.setStrDict(extra)
			d_2 = '' 
			d_2 += tce.serial_int(secs,d_2)
			m_1.paramstream += d_2
			r_4 = self.conn.sendMessage(m_1)
			if not r_4:
				raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	#extra must be map<string,string>
	def heartbeat(self,hello,timeout=None,extra={}):
		# function index: idx_4
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 2
		m_1.opidx = 2
		m_1.extra.setStrDict(extra)
		d_2 = '' 
		d_2 = tce.serial_string(hello,d_2)
		m_1.paramstream += d_2
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
	
	def heartbeat_async(self,hello,async,cookie=None,extra={}):
		# function index: idx_4
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 2
		m_1.opidx = 2
		m_1.extra.setStrDict(extra)
		d_3 = '' 
		d_3 = tce.serial_string(hello,d_3)
		m_1.paramstream += d_3
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ServerPrx.heartbeat_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def heartbeat_asyncparser(m,m2):
		# function index: idx_4 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			if r_6:
				user_2(prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	def heartbeat_oneway(self,hello,extra={}):
		# function index: idx_4
		
		try:
			m_1 = tce.RpcMessageCall(self)
			m_1.ifidx = 2
			m_1.opidx = 2
			m_1.calltype |= tce.RpcMessage.ONEWAY
			m_1.prx = self
			m_1.conn = m_1.prx.conn
			m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
			m_1.extra.setStrDict(extra)
			d_2 = '' 
			d_2 = tce.serial_string(hello,d_2)
			m_1.paramstream += d_2
			r_4 = self.conn.sendMessage(m_1)
			if not r_4:
				raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	#extra must be map<string,string>
	def bidirection(self,timeout=None,extra={}):
		# function index: idx_4
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 2
		m_1.opidx = 3
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
	
	def bidirection_async(self,async,cookie=None,extra={}):
		# function index: idx_4
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 2
		m_1.opidx = 3
		m_1.extra.setStrDict(extra)
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ServerPrx.bidirection_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def bidirection_asyncparser(m,m2):
		# function index: idx_4 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			if r_6:
				user_2(prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	def bidirection_oneway(self,extra={}):
		# function index: idx_4
		
		try:
			m_1 = tce.RpcMessageCall(self)
			m_1.ifidx = 2
			m_1.opidx = 3
			m_1.calltype |= tce.RpcMessage.ONEWAY
			m_1.prx = self
			m_1.conn = m_1.prx.conn
			m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
			m_1.extra.setStrDict(extra)
			r_4 = self.conn.sendMessage(m_1)
			if not r_4:
				raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	

class ITerminal(tce.RpcServantBase):
	# -- INTERFACE -- 
	def __init__(self):
		tce.RpcServantBase.__init__(self)
		if not hasattr(self,'delegatecls'):
			self.delegatecls = {}
		self.delegatecls[3] = ITerminal_delegate
	
	def onMessage(self,message,ctx):
		pass
	

class ITerminal_delegate:
	def __init__(self,inst,adapter,conn=None):
		self.index = 3
		self.optlist={}
		self.id = '' 
		self.adapter = adapter
		self.optlist[0] = self.onMessage
		
		self.inst = inst
	
	def onMessage(self,ctx):
		tce.log_debug("callin (onMessage)")
		d = ctx.msg.paramstream 
		idx = 0
		_p_message,idx = tce.unserial_string(d,idx)
		cr = None
		self.inst.onMessage(_p_message,ctx)
		if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True
		d = '' 
		m = tce.RpcMessageReturn(self.inst)
		m.sequence = ctx.msg.sequence
		m.callmsg = ctx.msg
		m.ifidx = ctx.msg.ifidx
		m.call_id = ctx.msg.call_id
		m.conn = ctx.msg.conn
		m.extra = ctx.msg.extra
		if d: m.paramstream += d
		ctx.conn.sendMessage(m)
		return True
	
	
class ITerminalPrx(tce.RpcProxyBase):
	# -- INTERFACE PROXY -- 
	def __init__(self,conn):
		tce.RpcProxyBase.__init__(self)
		self.conn = conn
		self.delta = None
		pass
	
	@staticmethod
	def create(ep,af= tce.AF_WRITE | tce.AF_READ):
		ep.open(af)
		conn = ep.impl
		proxy = ITerminalPrx(conn)
		return proxy
	
	@staticmethod
	def createWithEpName(name):
		ep = tce.RpcCommunicator.instance().currentServer().findEndPointByName(name)
		if not ep: return None
		conn = ep.impl
		proxy = ITerminalPrx(conn)
		return proxy
	
	@staticmethod
	def createWithProxy(prx):
		proxy = ITerminalPrx(prx.conn)
		return proxy
	
	#extra must be map<string,string>
	def onMessage(self,message,timeout=None,extra={}):
		# function index: 3
		
		m_1 = tce.RpcMessageCall(self)
		m_1.ifidx = 3
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		d_2 = '' 
		d_2 = tce.serial_string(message,d_2)
		m_1.paramstream += d_2
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		r_4 = self.conn.sendMessage(m_1)
		if not r_4:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()
		m_5 = None
		try:
			m_5 = m_1.mtx.get(timeout=timeout)
		except:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)
		if m_5.errcode != tce.RpcConsts.RPCERROR_SUCC:
			raise tce.RpcException(m_5.errcode)
		m_1 = m_5
	
	def onMessage_async(self,message,async,cookie=None,extra={}):
		# function index: 3
		
		ecode_2 = tce.RpcConsts.RPCERROR_SUCC
		m_1 = tce.RpcMessageCall(self)
		m_1.cookie = cookie
		m_1.ifidx = 3
		m_1.opidx = 0
		m_1.extra.setStrDict(extra)
		d_3 = '' 
		d_3 = tce.serial_string(message,d_3)
		m_1.paramstream += d_3
		m_1.prx = self
		m_1.conn = m_1.prx.conn
		m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
		m_1.async = async
		m_1.asyncparser = ITerminalPrx.onMessage_asyncparser
		r_5 = self.conn.sendMessage(m_1)
		if not r_5:
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	
	@staticmethod
	def onMessage_asyncparser(m,m2):
		# function index: 3 , m2 - callreturn msg.
		
		stream_1 = m2.paramstream
		user_2 = m.async
		prx_3 = m.prx
		if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return 
		try:
			idx_4 = 0
			d_5 = stream_1
			r_6 = True
			if r_6:
				user_2(prx_3,m.cookie)
		except:
			traceback.print_exc()
		
	
	def onMessage_oneway(self,message,extra={}):
		# function index: idx_4
		
		try:
			m_1 = tce.RpcMessageCall(self)
			m_1.ifidx = 3
			m_1.opidx = 0
			m_1.calltype |= tce.RpcMessage.ONEWAY
			m_1.prx = self
			m_1.conn = m_1.prx.conn
			m_1.call_id = tce.RpcCommunicator.instance().currentServer().getId()
			m_1.extra.setStrDict(extra)
			d_2 = '' 
			d_2 = tce.serial_string(message,d_2)
			m_1.paramstream += d_2
			r_4 = self.conn.sendMessage(m_1)
			if not r_4:
				raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
		except:
			traceback.print_exc()
			raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)
	

