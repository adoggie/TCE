#coding:utf-8

import common

class Java(common.Language):
	language = 'java'
	class Builtin:
		@classmethod
		def defaultValue(cls,this):
			r = '""'    #  as 'string'
			if this.type in ('byte','short','int','long','float','double'):
				r = '0'
			elif this.type == 'bool':
				r = 'false'
			return r

		@classmethod
		def typeName(cls,this):
			r = ''
			type = this.type
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

	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			if this.type.name == 'byte':
				return 'new byte[0]'
			return 'new Vector<%s>()'%this.type.getMappingTypeName(call_module)

		@classmethod
		def typeName(cls,this,call_module):
			if this.type.name == 'byte':
				return 'byte[]'
			return 'Vector<%s>'%this.type.getMappingTypeName(call_module)


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'new HashMap<%s,%s>()'%(this.first.getMappingTypeName(call_module),
											 this.second.getMappingTypeName(call_module)
											)

		@classmethod
		def typeName(cls,this,call_module):
			return 'HashMap< %s,%s >'%(this.first.getMappingTypeName(call_module),
			                        this.second.getMappingTypeName(call_module) )


	class Struct:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'new %s()'%this.getTypeName(call_module)

		@classmethod
		def typeName(cls,this,call_module):
			r = this.name
			if this.module:
				r = '%s.%s'%(this.module,this.name)
			return r

	class Module:
		def __init__(self,m):
			self.m = m


