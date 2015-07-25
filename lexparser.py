#--coding:utf-8--


#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

import	sys

language = 'py'
arch = '32'
lang_kws=[]

class SyntexTreeNode:
	def __init__(self,name):
		self.name = None

class Container:
	def __init__(self,name=''):
#		SyntexTreeNode.__init__(self,name)
		self.children={}
		self.list=[]
		self.name = name
		
	def addChild(self,c):
		#self.children.append(c)
		self.children[c.name] = c
		self.list.append(c)
	
	def createStruct(self,st):
		pass
		
	def createInterface(self,ifc):
		pass
		
	def createSequence(self,seq):
		pass
		
	def createDictionary(self,dict):
		pass
	
	def createEnumeration(self,enm):
		pass
	
	def createUnit(self,unit):
		pass
	

		
	
		
class Contained:
	def __init__(self,container=None):
		self.container =container
		
class TypeId:
	def __init__(self,type,id): #变量定义  type id;
		self.type = type # int name  , <int> is type, <name> is id
		self.id = id

	def getModuleName(self):
		parts = self.type.split('::')
		if len(parts)>1:
			return parts[-2]
		return ''

class TypeBase:
	def __init__(self,name):
		self.name = name
		self.idx = 0 #索引，用于数据序列化时类型识别
		#self.type = name
		self.module=''

	def getName(self):
		return self.name

	def getTypeName(self,call_module):
		#- builtin 类型无需添加 module 前缀
		# - 在同一module中的类型调用,此刻无需添加 module 前缀
		if call_module.name == self.module:
			if language == 'objc':
				return '%s*'%self.name
			return self.name

		if language == 'py':
			if self.module:
				return '%s.%s'%(self.module,self.name)
		if language =='as':
			if self.module:
				return '%s.%s'%(self.module,self.name)
		if language =='cpp':
			if self.module:
				return '%s::%s'%(self.module,self.name)
		if language =='java':
			if self.module:
				return '%s.%s'%(self.module,self.name)
		if language =='js':
			return '%s.%s'%(self.module,self.name)

		if language == 'objc':
			return '%s *'%self.name

		return self.name

	def getTypeDefaultValue(self,call_module):
		if language == 'py':
			return '%s()'%self.getTypeName(call_module)
		if language =='as':
			return 'new %s()'%self.getTypeName(call_module)
		if language =='cpp':
			return '%s()'%self.getTypeName(call_module)
		if language =='java':
			return 'new %s()'%self.getTypeName(call_module)
		if language =='js':
			return 'new %s()'%self.getTypeName(call_module)

		if language == 'objc':
			return '[%s new]'%self.getTypeName(call_module).replace('*','')

	def getMappingTypeName(self,call_module):
		# r = self.name
		return self.getTypeName(call_module)

		
class DataMember(Contained):
	def __init__(self,d,container): # d - type_id
		Contained.__init__(self,container)
		self.d = d
		self.name = d.id
		self.type = d.type
	
class Sequence(Contained,TypeBase):
	def __init__(self,name,type):
		TypeBase.__init__(self,name)
		self.type = type # sequence<type> name;
		self.valuetype = type

	def getTypeDefaultValue(self,call_module):
		if language == 'py':
			if self.type.name == 'byte':
				return "''"
			else:
				return '[]'
		if language == 'as':
			return 'new Array()'
		if language =='cpp':
			return 'std::vector< %s >()'%self.type.getMappingTypeName(call_module)
		if language =='java':
			if self.type.name == 'byte':
				return 'new byte[0]'

			return 'new Vector<%s>()'%self.type.getMappingTypeName(call_module)
		if language =='js':
			if self.type.name == 'byte':
				return 'new ArrayBuffer(0)'

			return '[]'
		if language =='objc':
			if self.type.name =='byte':
				return '[NSData new]'
			return '[NSMutableArray new]'

	def getMappingTypeName(self,call_module):
		r = ''
		if language == 'as':
			r = 'Array'
		if language =='cpp':
			return 'std::vector< %s >'%self.type.getMappingTypeName(call_module)
		if language =='java':
			if self.type.name == 'byte':
				return 'byte[]'
			return 'Vector<%s>'%self.type.getMappingTypeName(call_module)
		if language =='js':
			r = 'Array'
			if self.type.name == 'byte':
				r = 'ArrayBuffer'

		if language == 'objc':
			r = 'NSMutableArray*'
			if self.type.name == 'byte':
				r = 'NSData*'

		return r
		
class Dictionary(Contained,TypeBase):
	def __init__(self,name,first,second):
		TypeBase.__init__(self,name)
		self.first = first
		self.second = second

	def getTypeDefaultValue(self,call_module):
		if language =='py':
			return '{}'
		if language == 'as':
			return 'new HashMap()'

		if language == 'cpp':
			#return 'boost::shared_ptr< std::map<%s,%s> >( new std::map<%s,%s>()) '%(self.first.name,self.second.name,self.first.name,self.second.name)
#			return '%s::hash_type()'%self.name
			return 'std::map< %s,%s >()'%(self.first.getMappingTypeName(call_module),self.second.getMappingTypeName(call_module))
		if language =='java':
			return 'new HashMap<%s,%s>()'%(self.first.getMappingTypeName(call_module),
											 self.second.getMappingTypeName(call_module)
											)
		if language == 'js':
			return '{}'

		if language == 'objc':
			return '[NSMutableDictionary new]'

	def getMappingTypeName(self,call_module):
		r = ''
		if language == 'as':
			r = 'HashMap'
		if language =='cpp':
#			return 'boost::shared_ptr< std::map<%s,%s> >'%(self.first.name,self.second.name)
#			return '%s::hash_type'%(self.name)
			r = 'std::map< %s,%s >'%(self.first.getMappingTypeName(call_module),self.second.getMappingTypeName(call_module) )

		if language == 'java':
			r = 'HashMap< %s,%s >'%(self.first.getMappingTypeName(call_module),self.second.getMappingTypeName(call_module) )

		if language == 'objc':
			r = 'NSMutableDictionary*'


		return r

class Enumeration(Contained,TypeBase):
	def __init__(self,name):
		TypeBase.__init__(name)
		
class OperateMember(Contained):
	"""
	接口函数
	"""
	def __init__(self,name,type,params):
		self.name = name		#函数名称
		self.type = type 		#返回值类型   [ type  foo(params) ]
		self.params = params	#形参集合
		pass
		
class Struct(Container,Contained,TypeBase):
	def __init__(self,name):
		Container.__init__(self)
		Contained.__init__(self)
		TypeBase.__init__(self,name)
		
	def createDataMember(self,dm):
		if self.children.has_key(dm.id):
			return False
		e = DataMember(dm,self)
		self.children[dm.id] = e
		self.list.append(e)
		return True

#@2013.9.9
class Module(Container,Contained):
	def __init__(self,name):
		Container.__init__(self)
		Contained.__init__(self)
		self.name = name
		self.ref_modules = {} #引用到的其他module

	def __str__(self):
		return 'Module:%s'%self.name

	
class Interface(Container,Contained,TypeBase):
	def __init__(self,name):
		Container.__init__(self)
		Contained.__init__(self)
		TypeBase.__init__(self,name)
		self.ifidx = None
		self.delegate_exposed = None
		self.superif = None # 基接口
		self.opms=[]


	
	def createOperateMember(self,opm,ifname='',t=None):

		if self.children.has_key(opm.name):
			print 'error: multiple functions : <%s> be defined! line:%s interface:: <%s> function:<%s>'%(opm.name,t,self.name,opm.name)
			sys.exit()
			return False

		if self.hasOperateNameWithUp(opm.name):
			print 'error:  functions :<%s>  has been defined in super interface line:%s interface:<%s> function:<%s>'%(opm.name,t,self.name,opm.name)
			sys.exit()
			return False

		self.children[opm.name] = opm
		self.list.append(opm)

		return True

	#判别接口名是否存在
	def getOperateMember(self,name):
		return self.children.get(name)

	def hasOperateNameWithUp(self,name):
		'''
			判别本接口以及父接口是否存在相同的接口名称
		'''
		if self.getOperateMember(name):
			return True
		superif = self.superif
		while superif:
			if superif.hasOperateNameWithUp(name):
				return True
			superif = superif.superif
		return False

	def getOperateNames(self):
		return self.children.keys()

class Unit(Container):
	def __init__(self):
		Container.__init__(self)
		pass
		
	
class Builtin(TypeBase):
	def __init__(self,type):
		TypeBase.__init__(self,type)
		self.type = type
	
	tables =[
			'byte',
			'bool',
			'short',
			'int',
			'long',
			'float',
			'double',
			'string',
			]

	@staticmethod
	def isBuiltinType(type):
		return Builtin.tables.count(type)

	def getTypeDefaultValue(self,call_module):
		r = 'None'
		type = self.type
		if type in ('byte','short','int','long'):
			r = '0'
			if language == 'java':
				if type == 'byte':
					#r= '%s.valueOf( (byte)0)'%self.getMappingTypeName()
					r = '0'
				elif type =='short':
					r = '%s.valueOf((short)0)'%self.getMappingTypeName(call_module)
				else:
					r = '%s.valueOf(0)'%self.getMappingTypeName(call_module)
		elif type in ('float','double'):
			r = '0.0'
			if language == 'java':
				r = '%s.valueOf(0)'%self.getMappingTypeName(call_module)

		elif type in ('bool'):
			r = 'False'
			if language in ('as','cpp','js'):
				r = 'false'
#			if language == 'cpp':
#				r = 'false'
			if language == 'java':
				r = '%s.valueOf(false)'%self.getMappingTypeName(call_module)

		elif type in ('string'):
			r = "''"
			if language in ('as','cpp','java'):
				r ="\"\""
#			if language =='cpp':
#				r = "\"\""

		if language == 'objc':
			r = '0'
			if type == 'string':
				r = '@""'
		return r

	def getMappingTypeName2(self,call_module):
		r = 'Undefined'
		if language == 'objc':
			type = self.type
			r = 'NSNumber*'

			# if type in ('byte',) : #'bool'):
			# 	r ='uint8_t'
			# if type in ('bool',):
			# 	r = 'bool'
			# if type in ('short',):
			# 	r ='int16_t'
			# if type in ('int',):
			# 	r = 'int32_t'
			# elif type in ('float',):
			# 	r = type
			# elif type in ('long',):
			# 	r = type
			# elif type in ('double',):
			# 	r = type
			if type in ('string'):
				r = "NSString*"
			# elif type in ('void'):
			# 	r ='void'
		return r

	def getMappingTypeName(self,call_module):
		r = '-^|^*'*5
		if language in ('py','js','python'):
			r = ''

		if language == 'as':
			type = self.type
			if type in ('byte',) : #'bool'):
				r ='uint'
			if type in ('bool',):
				r = 'Boolean'
			if type in ('short','int'):
				r = 'int'
			elif type in ('float','long','double'):
				r = 'Number'
			elif type in ('string'):
				r = "String"
			elif type in ('void'):
				r ='void'

		if language == 'cpp':
			type = self.type

			if type in ('byte',) : #'bool'):
				r ='unsigned char'
			if type in ('bool',):
				r = 'bool'
			if type in ('short',):
				r ='short'
			if type in ('int',):
				r = 'int'
			elif type in ('float',):
				r = type
			elif type in ('long',):
				r = type
				if arch =='32':
					r = 'long long'
			elif type in ('double',):
				r = type
			elif type in ('string'):
				r = "std::string"
			elif type in ('void'):
				r ='void'

		if language == 'objc':
			type = self.type
			r = 'NSNumber*'
			if type in ('byte',) : #'bool'):
				r ='uint8_t'
			if type in ('bool',):
				r = 'bool'
			if type in ('short',):
				r ='int16_t'
			if type in ('int',):
				r = 'int32_t'
			elif type in ('float',):
				r = type
			elif type in ('long',):
				r = type
			elif type in ('double',):
				r = type
			elif type in ('string'):
				r = "NSString *"
			elif type in ('void'):
				r ='void'

		if language == 'java':
			type = self.type

			if type in ('byte',) : #'bool'):
				r ='Byte'
			if type in ('bool',):
				r = 'Boolean'
			if type in ('short',):
				r ='Short'
			if type in ('int',):
				r = 'Integer'
			elif type in ('float',):
				r = 'Float'
			elif type in ('long',):
				r = 'Long'

			elif type in ('double',):
				r = 'Double'
			elif type in ('string'):
				r = "String"
			elif type in ('void'):
				r ='void'

		return r

	@staticmethod
	def id(name):
		pass

	@staticmethod
	def str(id_):
		pass
		
types_def={}

kwds=['struct',
	  'interface',
	  'sequence',
	  'dictionary',
	  'exception',
	  'void',
	  'module'
	  ]
global_types_defs={}
global_ifs_defs={}

global_modules_defs={}
global_modules=[]

def register_global_types_def(module,type_,inst):
	global_types_defs['%s::%s'%(module,type_)] = inst

def register_global_ifs_def(module,type_,inst):
	global_ifs_defs['%s::%s'%(module,type_)] = inst

#def getTypeDef(type):
#	t = types_def.get(type,None)
#	return t

#根据module名称查找
def getModuleDef(name):
	m = global_modules_defs.get(name,None)
	return m



#检测变量名称是否合法
def checkVariantName(name,all=True):
	if kwds.count(name):
		return False
	return True
#	if all:
#		if getTypeDef(name):
#			return False
#	return True

def initBuiltinTypes():
	for t in Builtin.tables:
		types_def[t] = Builtin(t)
		global_types_defs[t] = Builtin(t)

types_def['void'] = Builtin('void')

global_types_defs['void'] = Builtin('void')

initBuiltinTypes()
	
unit=None

curr_idl_path='abc'