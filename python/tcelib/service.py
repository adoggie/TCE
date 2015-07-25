# --coding:utf-8 --
__author__ = 'scott'

from tce import *

class RpcRouteInoutPair:
	def __init__(self):
		self.in_ = None # ep
		self.out = None

class RpcIfRouteDetail:
	CALL = 0
	RETURN = 1
	def __init__(self):
		self.ifx = 0
		self.calls = {} # {EP_IDX_in:ep}
		self.returns={} # {EP_IDX_in:ep}

	def getRouteInoutPair(self,route,epid):
		# route: 0 - call ; 1 - return
		r = self.calls
		if route == RpcIfRouteDetail.RETURN:
			r = self.returns
		return r.get(epid)



class InterfaceDef:
	def __init__(self):
		self.id = 0
		self.name=''

class ServiceDef:
	def __init__(self):
		self.name =''
		self.id = 0
		self.pattern=''
		self.ifs={} #{IF_IDX:if}


class LocalServer:
	def __init__(self,id='',name=''):
		self.id = id
		self.name = name
		self.service = None # ServiceDef
		self.routes = {}    #{IFIDX:{call:{in,out},return:{in,out}}}
		self.ep_reads={}    #{name:ep,...}
		self.ep_writes={}   #{name:ep,...}
		self.name_eps={}    #{name:ep,...}
		self.props={}

	def isLocalInterface(self,ifid):
		'''
			判别ifid是否是本地服务器接口
		'''
		if self.service:
			return ifid in self.service.ifs.keys()
		return False

	def getPropertyValue(self,name,val=None):
		return self.props.get(name,val)

	def findRoutePair(self,ifidx,epidx,af=AF_READ):
		pass

	def findEndPointByName(self,name):
		ep = self.name_eps.get(name)
#		print ep
		return ep

	def getId(self):
		return 0        # 服务器已不具备整型编号表示服务器标示
		#return self.id
		# if self.service:
		# 	return ( (self.service.id<<8)&0xffff) | (self.id&0xff)
		# return 0

	def getName(self):
		return self.name

	def getServiceId(self):
		if self.service:
			return self.service.id
		return 0

