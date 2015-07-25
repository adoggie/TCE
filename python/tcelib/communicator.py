#-- coding:utf-8 --
"""
name: RpcCommunicator.py
brief:
  通信器对象，系统运行全局通信管理器
author: scott
date:
revision:

"""
__author__ = 'scott'

import gevent
import gevent.queue
import gevent.pool
from xml.dom.minidom import  parseString as xmlParseString
import endpoint
from endpoint import RpcEndPoint
import log
from log import log_error,log_info,log_debug,log_warn,log_print
import utils
import message
from service import *


#通信器
class RpcCommunicator:
	def __init__(self):
		self.adapters={}
		self.ep_adapters={}

		self.mtxadapter = threading.Lock()
		self.threads=[]
		self.condmsg = threading.Condition()
		self.msglist=[]
		self.running = False
		self.localServerId = 0 #本地服务编号

		self.msg_q={}
		self.mtxmsg_q = threading.Lock()
		self.logger = None

		self.sequence=0
		self.props={
			'rpc_call_timeout':30,  #RPC 调用默认等待超时时间
		}
		self.server = LocalServer()
		self.mtx = threading.Lock()
		self.disp_queue = gevent.queue.Queue()
		self.pool = None
		self.__inited = False     #标示是否已经初始化
		self.conneventlistener = None

	def setConnectionEventListener(self,evtlistener):
		self.conneventlistener = evtlistener

	def getConnectionEventListener(self):
		return self.conneventlistener

	def sleep(self,secs):
		gevent.sleep(secs)

	def getRpcCallTimeout(self):
		return self.props['rpc_call_timeout']

	def setRpcCallTimeout(self,wait):
		self.props['rpc_call_timeout'] = wait

	def getProperties(self):
		return self.props

	def setProperty(self,name,value):
		self.props[name] = value
		return self

	def generateSeq(self):
		self.mtx.acquire()
		self.sequence+=1
		if self.sequence >0xffffff00:
			self.sequence = 1
		self.mtx.release()
		return self.sequence

	def getLogger(self):
		return self.logger


	def enqueueMsg(self,m):
		self.mtxmsg_q.acquire()
		self.msg_q[m.sequence] = m
		self.mtxmsg_q.release()

	def dequeueMsg(self,sequence):
		m = None
		self.mtxmsg_q.acquire()
		m = self.msg_q.get(sequence)
		if m:
			del self.msg_q[sequence]
		self.mtxmsg_q.release()
		return m


	def createAdapter(self,id,ep):
		'''
			mq: 找出ep对象，创建adapter，并将ep关联到adapter
			socket:
			ep (RpcEndPoint/str)

		'''

		adapter = None
		self.mtxadapter.acquire()
		adapter = self.adapters.get(id)
		if adapter:
			log_error('adapter id <%s> is existed! '%id)
			self.mtxadapter.release()
			return adapter
		self.mtxadapter.release()

		if isinstance(ep,str) or isinstance(ep,unicode):
			ep = self.currentServer().findEndPointByName(ep)

		if not ep:
			return None

		if ep.type == 'socket' or ep.type == endpoint.SOCKET:
			from conn_socket import RpcAdapterSocket
			adapter = RpcAdapterSocket(id,ep)
		elif ep.type == 'websocket' or  ep.type == endpoint.WEBSOCKET:
			from conn_websocket import RpcAdapterWebSocket
			adapter = RpcAdapterWebSocket(id,ep)
		elif ep.type in ('mq','easymq','qpidmq','qpid',endpoint.EASYMQ,endpoint.MQ,endpoint.QPIDMQ):
			from conn_mq import RpcAdapterMQ
			adapter = RpcAdapterMQ(id,ep)

		if adapter:
			self.mtxadapter.acquire()
			self.adapters[id] = adapter
			self.ep_adapters[ep.name] = adapter
			self.mtxadapter.release()
			adapter.start()
		return adapter

	def addAdapter(self,adapter):
		self.mtxadapter.acquire()
		self.adapters[adapter.id] = adapter
		self.mtxadapter.release()

	def findAdatperByEpIdx(self,epidx):
		self.mtxadapter.acquire()
		adapter = self.ep_adapters.get(epidx)
		self.mtxadapter.release()

	def getConnectionForProxy(self,name):
		ep = self.currentServer().findEndPointByName(name)
		if ep:
			return  ep.impl
		return None

	def dispatchMsg(self,m):
		self.disp_queue.put(m)

	def _task_queue(self):
		self.running = True
		while self.running:
			m = self.disp_queue.get()
			try:
				m.conn.dispatchMsg(m)
			except:
				traceback.print_exc()
		print '_task_queue exiting...'

	def shutdown(self):
		for adapter in self.adapters.values():
			adapter.stop()

		self.running = False


	_handle = None
	@classmethod
	def instance(cls):
		if not cls._handle:
			cls._handle = cls()
		return cls._handle

	def getServiceDetail(self,type_):
		svc = self.id_svcs.get(type_,None)
		return svc

	def currentServer(self):
		return self.server


	def init(self,server_id='localhost',poolsize=5):
		'''
			server_id - server name
			poolsize - number of dispatching thread
		'''

		if self.__inited:
			return self

		self.__inited = True
		self.server = None
		self.id_svcs={} #系统服务
		self.logger = log.Logger(server_id)
		self.logger.addHandler(log.stdout())
		self.server = LocalServer(name=server_id)
		self.pool = gevent.pool.Pool(poolsize)
		for n in range(poolsize):
			self.pool.spawn(self._task_queue)
		return self

	def __variantReplace(self,value,variants):
		for k,v in variants.items():
			pattern = '{%s}'%k
			value = value.replace(pattern,v)
		return value

	def getConnectionMQCollection(self):
		from conn_mq import RpcConnectionMQ_Collection
		return RpcConnectionMQ_Collection.instance()

	def initMQEndpoints(self,cfgfile):
		"""
		加载MQ端点配置项
		初始化 endpoints

		common_defs:
		  endpoints:
			- name: mq_client
			  host: dev1
			  port: 5672
			  address: mq_client;{create:always,node:{type:queue,durable:true}}
			  type: qpid

			- name: mq_server
			  host: dev1
			  port: 5672
			  address: mq_server;{create:always,node:{type:queue,durable:true}}
			  type: qpid

		client:
		  endpoints:
			- name: mq_client
			  af_mode: AF_WRITE
			- name: mq_server
			  af_mode: AF_READ

		  endpoint_pairs:
			- call: mq_server
			  return: mq_client

		server:
		  endpoints:
			- name: mq_client
			  af_mode: AF_WRITE
			- name: mq_server
			  af_mode: AF_READ

		:param yamlcfg:
		:return:
		"""
		from conn_mq import RpcConnectionMQ_Collection
		import yaml
		f = open(cfgfile)
		props = yaml.load(f.read())
		f.close()

		eps = {}
		ep_defs = props['common_defs'].get('endpoints',[])
		for ep in ep_defs:
			name = ep['name']
			host = ep['host']
			port = ep['port']
			address = ep['address']
			type_ = ep['type']
			ep = RpcEndPoint(name=name,host=host,port=port,addr=address,type_=type_)
			eps[name] = ep

		server_name = self.currentServer().getName()
		server_defs = props[server_name]

		ep_defs = server_defs.get('endpoints',[])
		for ep in ep_defs:
			ep_inst = eps.get( ep['name'])
			af_mode = ep['af_mode'].lower()
			if af_mode == 'af_write':
				af_mode = AF_WRITE
			else:
				af_mode = AF_READ
			ep_inst.open( af_mode ) # mq connection has been added into  RpcConnectionMQ_Collection

		#-- endpoint_pairs
		pairs = server_defs.get('endpoint_pairs',[])
		for pair in pairs:
			conn_out = RpcConnectionMQ_Collection.instance().get( pair['call'] )
			conn_in = RpcConnectionMQ_Collection.instance().get( pair['return'])
			conn_out.setLoopbackMQ(conn_in)
		return self


	#打开消息路由功能,将读取服务配置文件,Communicator初始化之后可以调用
	def initMessageRoute(self,xmlfile=''):

		if not xmlfile:
			return False
		f = open(xmlfile)
		d = f.read()
		f.close()
		doc = xmlParseString(d)
		r = doc.documentElement

		#- 检索服务配置信息
		servername = self.server.getName()

		e = r.getElementsByTagName('InterfaceDef')
		if not e:
			log_error('Tag:InterfaceDef not defined!')
			return False
		ifs = e[0].getElementsByTagName('if')

		#接口类型定义
		ifxdefs={} #{name:ifx}
		for e in ifs:
			ifx = InterfaceDef()
			ifx.name = e.getAttribute('name')
			ifx.id = int(e.getAttribute('id'))
			ifxdefs[ifx.name] = ifx

		#--- VariantDefs ---

		variants={}
		e =  r.getElementsByTagName('VariantDef')[0]
		if e:
			e2 = e.getElementsByTagName('var')
			for e3 in e2:
				name = e3.getAttribute('name')
				value = e3.getAttribute('value')
				variants[name] = value

		#--- End VariantDefs ---


		# endpoints
		epdefs = {} #{EP_IDX:ep}

		e = r.getElementsByTagName('EndPoints')
		if not e:
			log_error('Tag: EndPoints not found!')
			return False
		e2 = e[0].getElementsByTagName('ep')
		epidx = 1
		for e in e2:
			ep = RpcEndPoint()          # 通信端点类
			ep.id = epidx
			ep.name = e.getAttribute('name')
			ep.type = e.getAttribute('type')

			#-- 变量替换  <VariantDef><var/></VariantDef>
			ep.host = e.getAttribute('host')
			ep.host = self.__variantReplace(ep.host,variants)

			ep.addr = e.getAttribute('address')
			ep.addr = self.__variantReplace(ep.addr,variants)

			ep.port = e.getAttribute('port')
			ep.port = self.__variantReplace(ep.port,variants)
			ep.port = int(ep.port)

			# print ep.host,ep.port

			ep.keyfile = e.getAttribute('keyfile').strip()
			ep.certfile = e.getAttribute('certfile').strip()
			s = e.getAttribute('compress').strip()
			if s:
				ep.compress = utils.intValueOfString(s,message.COMPRESS_ZLIB)

			epidx+=1
			epdefs[ep.name] = ep        # 记录通信端点

		# -- servers
		e = r.getElementsByTagName('servers')
		if not e:
			log_error('Tag: servers not found!')
			return False
		e2 = e[0].getElementsByTagName('server')
		for e in e2:
			if servername != e.getAttribute('name'):
				continue
			server = LocalServer()
			self.server = server
			server.name = e.getAttribute('name')
			'''
			type_ =  e.getAttribute('type')
			svc = svcdefs.get(type_)
			if not svc:
				log_error('service <%s> not defined!'%type_)
				return False
			server.service = svc
			server.id = int(e.getAttribute('id'))
			'''
			e3 = e.getElementsByTagName('route')
			for e4 in e3:
				route = RpcIfRouteDetail()
				ifname = e4.getAttribute('if')
				ifx = ifxdefs.get(ifname)
				if not ifx:
					log_error(' interface <%s> not defined!'%ifname)
					return False
				route.ifx = ifx

				e5 = e4.getElementsByTagName('call')        #RpcMsg CALL
				for e6 in e5:
					name = e6.getAttribute('in')
					ep = epdefs.get(name)
					inout = RpcRouteInoutPair()
					if not ep:
						print epdefs
						log_error('endpoint <%s> not defined!'%name)
						return False
					inout.in_ = ep
					server.ep_reads[ep.name] = ep   # cached ep
					server.name_eps[ep.name] = ep   # cached ep

					name = e6.getAttribute('out')
					ep = epdefs.get(name)
					if not ep:
						log_error('endpoint <%s> not defined!'%name)
						return False
					inout.out = ep
					server.ep_writes[ep.name] = ep  #cached ep
					server.name_eps[ep.name] = ep   #cached ep

					route.calls[inout.in_.id] = inout #id - increament value form 1

				e5 = e4.getElementsByTagName('return')   #RpcMsg RETURN
				for e6 in e5:
					name = e6.getAttribute('in')
					ep = epdefs.get(name)
					inout = RpcRouteInoutPair()
					if not ep:
						log_error('endpoint <%s> not defined!'%name)
						return False

					server.ep_reads[ep.name] = ep
					server.name_eps[ep.name] = ep
					inout.in_ = ep
					name = e6.getAttribute('out')
					ep = epdefs.get(name)
					if not ep:
						log_error('endpoint <%s> not defined!'%name)
						return False
					inout.out = ep
					server.ep_writes[ep.name] = ep
					server.name_eps[ep.name] = ep
					route.returns[inout.in_.id] = inout

				server.routes[route.ifx.id] = route  # cached route talbe of which interface
			#<extra_mqs/>
			els = e.getElementsByTagName('extra_mqs')
			if els:
				e5 = els[0]
				ins = e5.getAttribute('ins').strip().split(',')
				outs =e5.getAttribute('outs').strip().split(',')
				for name in ins:
					if not name.strip():continue
					ep = epdefs.get(name)
					if not ep:
						log_error('endpoint <%s> not defined!'%name)
						return False
					server.ep_reads[ep.name] = ep
					server.name_eps[ep.name] = ep

				for name in outs:
					if not name.strip():continue
					ep = epdefs.get(name)
					if not ep:
						log_error('endpoint: "%s" not defined!'%name)
						return False
					server.ep_writes[ep.name] = ep
					server.name_eps[ep.name] = ep

			#properties  app 的属性配置
			els = e.getElementsByTagName('properties')
			if els:
				e5 = els[0]
				for e6 in e5.getElementsByTagName('property'):
					name = e6.getAttribute('name')
					value = e6.getAttribute('value')
					self.server.props[name] = value



		if not self.server:
			log_error('localserver not defined!')
			return False

#		print self.server.name_eps
#		print self.server.mq_reads
#		print self.server.mq_writes

		#打开ep，如是mq的情况，立刻能获取消息，此刻未绑定adapter，所以消息无法map到对应的rpc函数
		for ep in self.server.ep_reads.values():
			#print ep
			if not ep.open(AF_READ):
				return False

		for  ep in self.server.ep_writes.values():

			if not ep.open(AF_WRITE):
				return False

		return True



	def run(self):
		return True

	def waitForShutdown(self):
		self.pool.join()

		# for adapter in self.adapters.values():
		# 	adapter.join()



	def getServiceReadMQName(self,svc_id):
		'''
			根据 服务器id获取 服务接收数据的mq名称
		'''
		mq = ''
		try:
			svc_id = int(svc_id)
			type,id = (svc_id>>8)&0x7f, svc_id&0xff #类型的最高位不用
			mq = ''
			svc = self.getServiceDetail(type)
			if svc:
				mq =svc.pattern%id
		except:
			traceback.print_exc()
		return mq

	handle = None
