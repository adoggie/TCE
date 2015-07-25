#--coding:utf-8--


'''
 2012.10.9
 1. 屏蔽connection 避免暴露给用户， sendMessage的同时建立网络连接

2014.6.21 scott
	1. RpcEndpoint 增加 compress ,默认为  ZLIB压缩
'''


import os,sys,os.path,struct,time,traceback,string,zlib,threading

# import utils



# from xml.dom.minidom import  parseString as xmlParseString
# import loggin
import gevent
# import gevent.queue
# import gevent.pool
#
# import gevent.lock
# import gevent.event

# from communicator import RpcCommunicator

DEBUG = True

RPCERROR_SUCC = 0
RPCERROR_SENDFAILED = 1
RPCERROR_TIMEOUT  =2
RPCERROR_DATADIRTY = 3
RPCERROR_INTERFACE_NOTFOUND = 4 		#adapter中无法定位到接口函数
RPCERROR_UNSERIALIZE_FAILED = 5 		#解析rpc参数失败
RPCERROR_REMOTEMETHOD_EXCEPTION = 6 	#rpc 远端服务函数调用异常



AF_NONE = 0x00
AF_READ = 0x01
AF_WRITE = 0x02


class RpcInternal:
	func_str = str
	func_type = type


class RpcConsts:
	RPCERROR_SUCC = 0
	RPCERROR_SENDFAILED =1
	RPCERROR_DATADIRTY= 3
	RPCERROR_TIMEOUT = 2
	RPCERROR_INTERFACE_NOTFOUND = 4
	RPCERROR_UNSERIALIZE_FAILED = 5
	RPCERROR_REMOTEMETHOD_EXCEPTION = 6
	RPCERROR_DATA_INSUFFICIENT = 7
	RPCERROR_REMOTE_EXCEPTION = 8

	RPCERROR_CONNECT_UNREACHABLE = 101
	RPCERROR_CONNECT_FAILED  = 102
	RPCERROR_CONNECT_REJECT = 103
	RPCERROR_CONNECTION_LOST = 104

	COMPRESS_NONE = 0
	COMPRESS_ZLIB = 1
	COMPRESS_BZIP2 = 2

	ENCRYPT_NONE = 0
	ENCRYPT_MD5  = 1
	ENCRYPT_DES  = 2

	MSGTYPE_RPC = 1
	MSGTYPE_NORPC = 2

	error_infos={
		RPCERROR_SUCC:"RPCERROR_SUCC",
		RPCERROR_SENDFAILED:"RPCERROR_SENDFAILED",
		RPCERROR_DATADIRTY:"RPCERROR_DATADIRTY",
		RPCERROR_TIMEOUT :"RPCERROR_TIMEOUT",
		RPCERROR_INTERFACE_NOTFOUND:"RPCERROR_INTERFACE_NOTFOUND",
		RPCERROR_UNSERIALIZE_FAILED:"RPCERROR_UNSERIALIZE_FAILED",
		RPCERROR_REMOTEMETHOD_EXCEPTION:"RPCERROR_REMOTEMETHOD_EXCEPTION",
		RPCERROR_DATA_INSUFFICIENT:"RPCERROR_DATA_INSUFFICIENT",
		RPCERROR_REMOTE_EXCEPTION:"RPCERROR_REMOTE_EXCEPTION",

		RPCERROR_CONNECT_UNREACHABLE:"RPCERROR_CONNECT_UNREACHABLE",
		RPCERROR_CONNECT_FAILED:"RPCERROR_CONNECT_FAILED",
		RPCERROR_CONNECT_REJECT:"RPCERROR_CONNECT_REJECT",
		RPCERROR_CONNECTION_LOST:"RPCERROR_CONNECTION_LOST"
	}



class RpcContext:
	def __init__(self):
		self.conn = None	#RpcConnection
#		self.sequence = 0 #一次调用产生的事务编号，调用和返回匹配的编号
		self.msg = None #调用消息 RpcMessageCall


class RpcException(Exception):
	def __init__(self,errcode,errmsg='',data=None):
		self.errcode = errcode
		self.errmsg = errmsg
		self.subcode = 0
		self.d = data

	def what(self):
		msg = self.errmsg
		if not msg:
			msg = RpcConsts.error_infos.get(self.errcode,"Undefined Error")
		return msg

	def __str__(self):
		return self.what()


def getUniqueSequence():
	from communicator import RpcCommunicator
	return RpcCommunicator.instance().generateSeq()



class Shortcuts:
	@staticmethod
	def USER_ID(ctx):
		userid = ctx.msg.extra.getValue('__user_id__')
		return userid

	@staticmethod
	def MQ_RETURN(ctx):
		return ctx.msg.extra.getValue('__mq_return__')


	@staticmethod
	def getExtraValue(ctx,name,default=None):
		return ctx.msg.extra.getValue(name)

	@staticmethod
	def CALL_USER_ID(userid,extra={}):
		import copy
		extra = copy.deepcopy(extra)
		if not extra:
			extra ={}
		extra['__user_id__'] = str(userid)
		return extra


class RpcMessageTraits:
	"""
	消息传送管理

	Proxy\Servant 都可以控制消息的传送有效时间
	对单个调用函数的处理可采用  MAX_LINGER_TIME() 作为 extra参数输入
	"""
	MAX_MSG_LINGER_TIME = '__linger_time__'
	def __init__(self):
		self.max_linger_time = 0 #对点接收消息的超时,默认：不控制


	def set_max_linger_time(self,seconds):
		"""
		控制 发送消息开始到接收消息 之间消息是否过时
		在MQ情景下，消息被发送到broker之后被持久化，等接收者读取消息时，消息可能已经过时
		所以在发送消息时对消息的生命存活时间进行控制
		:param seconds:
		:return:
		"""
		self.max_linger_time = seconds

	@classmethod
	def MAX_LINGER_TIME(cls,seconds,extra={}):
		'''
		在proxy的每一个发送消息时，设置消息到达有效时间
		   proxy.hello(text,RpcMessageTraits.MAX_LINGER_TIME(5,{'other_keys':'other_values'}) )
		:param seconds:
		:param extra:
		:return:
		'''
		data = {}
		if extra:
			data = extra.copy()
		data[RpcMessageTraits.MAX_MSG_LINGER_TIME] = seconds + int(time.time())
		return data


class RpcServantBase(RpcMessageTraits):
	def __init__(self):
		RpcMessageTraits.__init__(self)

class RpcProxyBase(RpcMessageTraits):
	def __init__(self):
		RpcMessageTraits.__init__(self)



def sleep(secs):
	gevent.sleep(secs)
	# time.sleep(secs)	#if gevent patched time

def currentServer():
	from communicator import RpcCommunicator
	return RpcCommunicator.instance().currentServer()

def waitForShutdown():
	from communicator import RpcCommunicator
	RpcCommunicator.instance().waitForShutdown()