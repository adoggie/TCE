# -- coding:utf-8 --


#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib
from errbase import *
from log import *
from tce import *
import serialize


'''
------------------
msghdr
cmdtxt
\0\0
二进制流
-----------------
视频包由三部分构成: MetaMessage数据元封套,控制命令文本(json格式),二进制数据，后两者之间采用连续两个\0区分，表示开始二进制流数据
[metamsg,cmdtxt,bindata]
bindata部分格式、编码由cmdtxt控制

# [magic,size,compress,encrypt,version],[command text(json)],[\0\0],[binary data..]
'''

'''
	< 100 不压缩
'''

COMPRESS_NONE = 0	#压缩方式ß
COMPRESS_ZLIB = 1
COMPRESS_BZIP2 = 2

ENCRYPT_NONE = 0  #加密方式
ENCRYPT_MD5  = 1
ENCRYPT_DES  = 2
ENCRYPT_AES  = 3

MSGTYPE_RPC = 1
MSGTYPE_NORPC = 2

class NetMetaPacket:
	def __init__(self,msg=None ):
		self.msg = msg
		self.size4 = 0
		self.encrypt1 = ENCRYPT_NONE	#加密算法
		self.ver4 = 0x01000000 			# means 1.0.0.0

	magic4=0xEFD2BB99
	
	@classmethod
	def minSize(cls):
		return 14
		
	def marshall(self,compress=COMPRESS_ZLIB):
		d = self.msg.marshall()
		if compress != COMPRESS_NONE:
			if len(d)>100:
				if compress == COMPRESS_ZLIB:
					d = zlib.compress(d)
					compress = COMPRESS_ZLIB	# zlib default
			else:
				compress = COMPRESS_NONE
		r = struct.pack('!BBI',compress,self.encrypt1,self.ver4)
		r+= d
		self.size4 = len(r)+4
		r = struct.pack('!II', self.magic4,self.size4) + r
		return r


class NetPacketQueue:
	def __init__(self,conn = None,size= 1024):
		self.size = size
		self.outs={}
		self.ins={}
		self.user=None
		self.conn = conn
		self.bf=''
		self.pktlist=[] #解出来的消息
		self.invalid = False

	def clearPackets(self):
		self.pktlist=[]

	def destroy(self):
		self.invalid = True

	def getMessageList(self):
		pkts = self.pktlist
		self.pktlist=[]
		return pkts

	'''
		@return: false - 脏数据产生
	'''
	def dataQueueIn(self,d):


		rc = (True,2) # 2表示ok
		self.bf+=d
		d = self.bf
		while True:
			hdrsize = NetMetaPacket.minSize()
			if len(d)<NetMetaPacket.minSize():
				rc = True,0 #数据不够,等待
				break

			magic,size,compress,encrypt,ver = struct.unpack('!IIBBI',d[:hdrsize])
			if magic != NetMetaPacket.magic4:
				return False, NETMSG_ERROR_MAGIC#
			if size<=10:
				return False,NETMSG_ERROR_SIZE
			if len(d)< size+4:
				rc = True,1 #数据不够
				break
			size-=10

			s = d[hdrsize:hdrsize+size]
			d = d[hdrsize+size:]
			if compress == COMPRESS_ZLIB:
				try:
					s = zlib.decompress(s)
				except:
					return False,NETMSG_ERROR_DECOMPRESS
			elif compress != COMPRESS_NONE:
				return False,NETMSG_ERROR_NOTSUPPORTCOMPRESS
			self.pktlist.append(s)
		self.bf = d
		return rc



class RpcExtraData:
	NODATA = 0  	# 0 表示没有附加数据，每种数据都可以自己标识自己
	BYTE_STREAM = 1 #字节流
	STRING=2
	STRING_DICT= 3
	STRING_LIST = 4

	def __init__(self):
#		self.type = RpcExtraData.NODATA
#		self.d = ''
		self.props={}

	def setStrDict(self,d):
		self.props = d

	def getStrDict(self):
		return self.props

	def setPropertyValue(self,name,value):
		self.props[name] = str(value)

	def getValue(self,name,dft=None):
		return self.props.get(name,dft)

#	def getStrList(self):
#		return None
#
#	def getString(self):
#		return None
#
#	def getBytes(self):
#		return self.d


	def marshall(self):
#		size = (self.type<<24)| (len(self.d)&0xffffff)
#		return struct.pack('!I',size) + self.d
		d = ''
		# print repr(self.props)

		if not self.props :
			self.props ={}
		d = struct.pack('!I',len(self.props))
		for k,v in self.props.items():
			d+=struct.pack('!I',len(k)) + k.encode('utf-8')	# 2014.7.2 scott
			d+=struct.pack('!I',len(v)) + v.encode('utf-8')
		return d


	def size(self):
		return self.datasize()+4

	def datasize(self):
		size = 0
		for k,v in self.props.items():
			size += len(k)+len(v)+8
		return size

	def unmarshall(self,stream):
#		size, = struct.unpack('!I',stream[:4])
#		self.type,size = (size>>24)&0xff,size&0xffffff
#		self.d = stream[4:size+4]
		p=0

		size, = struct.unpack('!I',stream[p:p+4])
		p+=4
		for n in range(size):
			size, = struct.unpack('!I',stream[p:p+4])
			p+=4
			key = stream[p:p+size]
			p+=size
			size, = struct.unpack('!I',stream[p:p+4])
			p+=4
			val = stream[p:p+size]
			p+=size
			self.props[key] = val




'''

magic|size|msgtype|seq|calltype|interface_idx|operate_idx|error_code|data

==========
magic -   'eeff'
size -	  数据包长度(包含magic)
compress - 压缩方式 0 - 不压缩  ; 1 - zlib ; 2 - bzip
encrypt - 加密方式
ver - 消息版本

msgtype (1) - 1 : RPC
		  2 ~ 用户定义信息
seq - (4)  调用事务序号
calltype (1) - 0x01 ： call 调用方法
	       0x02 ： return 返回参数
	       0x10 ： twoway 调用方法
	       0x20 ： onway 单向调用
interface_idx (2) - 接口索引编号  (0 - 返回值类型)
operate_idx (2) - 接口函数索引编号 (0 - 返回值类型)
param_size (1)  -  参数个数
data - 参数值内容

'''


class RpcMessage:

	CALL = 0x01
	RETURN = 0x02
	TWOWAY = 0x10
	ONEWAY = 0x20
	ASYNC = 0x40

	DEFAULT_CALL = CALL | TWOWAY	#默认调用等待方式

	def __init__(self,traits = None):
		from gevent.event import AsyncResult

#		self.params=[]

		self.type =  MSGTYPE_RPC #
		self.sequence = 0
		self.calltype = RpcMessage.DEFAULT_CALL
		self.ifidx = 0 	#接口类编号 uint16
		self.opidx = 0 	#函数编号	uint16
		# self.ifname = '' #接口名称
		# self.opname = '' #函数名称
		self.errcode = RPCERROR_SUCC # RETURN 包 会使用到错误码
		self.paramsize = 0  # byte 宽度
		self.call_id = 0  # 调用者编号   第15位 0 - 本地发起RPC， 1 - 转向的RPC；第14-8位 服务类型编号 ; 第7-0 服务id编号
		self.extra = RpcExtraData()   #额外数据
		#--以下成员用于接收解析临时存储

		self.paramstream = ''
		self.mtx = AsyncResult() #utils.MutexObject()
		self.prx = None
		self.async = None #异步通知函数 异步调用时使用
		self.asyncparser = None #异步返回值解析出参数对象传递到 async
		self.conn = None  # which RpcConnection object

#		self.attr = None # mq'attr
		self.callmsg = None
		self.user_id = 0
		self.cookie = None # 异步调用本地传递到回调函数的用户变量  2013.11.30

		self.traits = traits
		# self.async( self.asyncparser( streamdata) )

	def __str__(self):
		return 'type:%s,sequence:%s,calltype:%s,ifidx:%s,opidx:%s,errcode:%s'%(self.type,self.sequence,
		self.calltype,self.ifidx,self.opidx,self.errcode)

#	#添加参数数据进去
#	def addParam(self,p):
#		self.params.append(p)

	# 打包Rpc消息包，讲序列化的参数打包成自己流
	def marshall(self):
		"""
		type,sequence,calltype,ifidx,opidx,error,paramsize,call_id,ifname,opname,extra_data,content
		:return:
		"""
		d = struct.pack('!BIBHHIBH',self.type,
						self.sequence,
						self.calltype,
						self.ifidx,
						self.opidx,
						self.errcode,	# 2012.9.9 错误码
						self.paramsize,
						self.call_id
						)
		#todo. 暂时不添加接口和函数名称标识到消息控制
		# d = serialize.serial_string_8(self.ifname,d)
		# d = serialize.serial_string_8(self.opname,d)

		d+= self.extra.marshall()
		d+= self.paramstream
		return d

	@classmethod
	def unmarshall(cls,d):
		m = None
		try:
			idx = 0
			m = RpcMessage()
			m.type, = struct.unpack('B',d[idx:idx+1])
			idx+=1
			m.sequence, = struct.unpack('!I',d[idx:idx+4])
			idx+=4
			m.calltype, = struct.unpack('B',d[idx:idx+1])
			idx+=1
			m.ifidx, = struct.unpack('!H',d[idx:idx+2])
			idx+=2
			m.opidx, = struct.unpack('!H',d[idx:idx+2])
			idx+=2
			m.errcode, = struct.unpack('!I',d[idx:idx+4])
			idx+=4
			m.paramsize, = struct.unpack('B',d[idx:idx+1])
			idx+=1
			m.call_id, = struct.unpack('!H',d[idx:idx+2])
			idx+=2
			m.extra.unmarshall(d[idx:])
			idx+=m.extra.size()
			m.paramstream = d[idx:]
			# m.user_id = int( m.extra.getValue("__user_id__","0"))
			m.user_id =  m.extra.getValue("__user_id__","0")
#			print m.extra.props,repr(m.paramstream)
		except :
			log_error(traceback.format_exc())
			m = None
		return m

#调用消息
class RpcMessageCall(RpcMessage):
	def __init__(self,traits = None):
		RpcMessage.__init__(self,traits)
		self.sequence = getUniqueSequence()
		self.calltype = RpcMessage.CALL


#返回消息包
class RpcMessageReturn(RpcMessage):
	def __init__(self,traits = None):
		RpcMessage.__init__(self,traits)
		self.calltype = RpcMessage.RETURN
		# self.delegate = delegate	# 2015.7.5 scott




		
if __name__=='__main__':
	#print NetMetaPacket(msg=MsgCallReturn(value=range(10),bin='abc' ),compress=COMPRESS_NONE).marshall()
	#print NetMetaPacket.minSize()
	# m = MsgCallReturn()
	# m['name']='scott'
	# print m.attrs
	#
	pass