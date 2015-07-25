#--coding:utf-8--


#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

import	sys

language = 'py'
arch = '32'

class SyntexTreeNode:
	def __init__(self,name):
		self.name = None

class Container:
	def __init__(self,name=''):
#		SyntexTreeNode.__init__(self,name)
		self.children={}
		self.list=[]
		
	def addChild(self,c):
		#self.children.append(c)
		self.children[c.getName()] = c
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


class TypeBase:
	def __init__(self,name):
		self.name = name
		self.idx = 0 #索引，用于数据序列化时类型识别
		#self.type = name

	def getName(self):
		return self.name

	def getTypeDefaultValue(self):
		if language == 'py':
			return '%s()'%self.name
		if language =='as':
			return 'new %s()'%self.name
		if language =='cpp':
			return '%s()'%self.name
		if language =='java':
			return 'new %s()'%self.name

	def getMappingTypeName(self):
		r = self.name

		return r
		
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

	def getTypeDefaultValue(self):
		if language == 'py':
			return '[]'
		if language == 'as':
			return 'new Array()'
		if language =='cpp':
			return 'std::vector< %s >()'%self.type.getMappingTypeName()
		if language =='java':
			return 'new Vector<%s>()'%self.type.getMappingTypeName()

	def getMappingTypeName(self):
		r = ''
		if language == 'as':
			r = 'Array'

		if language =='cpp':
			return 'std::vector< %s >'%self.type.getMappingTypeName()
		if language =='java':
			return 'Vector<%s>'%self.type.getMappingTypeName()

		return r
		
class Dictionary(Contained,TypeBase):
	def __init__(self,name,first,second):
		TypeBase.__init__(self,name)
		self.first = first
		self.second = second

	def getTypeDefaultValue(self):
		if language =='py':
			return '{}'
		if language == 'as':
			return 'new HashMap()'

		if language == 'cpp':
			#return 'boost::shared_ptr< std::map<%s,%s> >( new std::map<%s,%s>()) '%(self.first.name,self.second.name,self.first.name,self.second.name)
#			return '%s::hash_type()'%self.name
			return 'std::map< %s,%s >()'%(self.first.getMappingTypeName(),self.second.getMappingTypeName())
		if language =='java':
			return 'new Hashtable<%s,%s>()'%(self.first.getMappingTypeName(),
											 self.second.getMappingTypeName()
											)


	def getMappingTypeName(self):
		r = ''
		if language == 'as':
			r = 'HashMap'
		if language =='cpp':
#			return 'boost::shared_ptr< std::map<%s,%s> >'%(self.first.name,self.second.name)
#			return '%s::hash_type'%(self.name)
			r = 'std::map< %s,%s >'%(self.first.getMappingTypeName(),self.second.getMappingTypeName() )

		if language == 'java':
			r = 'Hashtable< %s,%s >'%(self.first.getMappingTypeName(),self.second.getMappingTypeName() )

		return r

class Enumeration(Contained,TypeBase):
	def __init__(self,name):
		TypeBase.__init__(name)
		
class OperateMember(Contained):
	def __init__(self,name,type,params):
		self.name = name
		self.type = type # callreturn  [ type  foo(params) ]
		self.params = params
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
		
	
	
class Interface(Container,Contained,TypeBase):
	def __init__(self,name):
		Container.__init__(self)
		Contained.__init__(self)
		TypeBase.__init__(self,name)


	
	def createOperateMember(self,opm):

		if self.children.has_key(opm.name):
			return False
		self.children[opm.name] = opm
		self.list.append(opm)

		return True
		
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

	def getTypeDefaultValue(self):
		r = 'None'
		type = self.type
		if type in ('byte','short','int','long'):
			r = '0'
			if language == 'java':
				if type == 'byte':
					#r= '%s.valueOf( (byte)0)'%self.getMappingTypeName()
					r = '0'
				else:
					r = '%s.valueOf(0)'%self.getMappingTypeName()

		elif type in ('float','double'):
			r = '0.0'
			if language == 'java':
				r = '%s.valueOf(0)'%self.getMappingTypeName()

		elif type in ('bool'):
			r = 'False'
			if language in ('as','cpp'):
				r = 'false'
#			if language == 'cpp':
#				r = 'false'
			if language == 'java':
				r = '%s.valueOf(false)'%self.getMappingTypeName()

		elif type in ('string'):
			r = "''"
			if language in ('as','cpp','java'):
				r ="\"\""
#			if language =='cpp':
#				r = "\"\""

		return r

	def getMappingTypeName(self):
		r = '-^|^*'*5

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
	  'void'
	  ]

def getTypeDef(type):
	t = types_def.get(type,None)
	return t

#检测变量名称是否合法
def checkVariantName(name,all=True):
	if kwds.count(name):
		return False
	if all:
		if getTypeDef(name):
			return False
	return True

def initBuiltinTypes():
	for t in Builtin.tables:
		types_def[t] = Builtin(t)

types_def['void'] = Builtin('void')

initBuiltinTypes()
	
unit=None

