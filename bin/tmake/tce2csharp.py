#--coding:utf-8--


#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
# #java rpc二进制包装
#数据传输不采用xml，底部socket通信，协议为tce的二进制rpc格式
#2012.12.10 updated

# 2012.12.10
#   1. add extradata parameter in proxy method
#	2. code trim

import os
import os.path
import string

import lexparser
from lexparser import *
from mylex import syntax_result,parse_idlfile

interface_idx = [ ]
idx_datatype=1
idx_interface = 1
dataMapStream =0
NEWLINE = '\n'


ostream = sys.stdout

headtitles='''
#---------------------------------
#  - TCE -
#  Tiny Communication Engine
#
#  sw2us.com copyright @2012
#  bin.zhang@sw2us.com / qq:24509826
#---------------------------------

'''+NEWLINE


class LanguageCSharp(object):
	language = 'csharp'
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
				r ='byte'
			if type in ('bool',):
				r = 'bool'
			if type in ('short',):
				r ='short'
			if type in ('int',):
				r = 'int'
			elif type in ('float',):
				r = 'float'
			elif type in ('long',):
				r = 'long'
			elif type in ('double',):
				r = 'double'
			elif type in ('string',):
				r = "string"
			elif type in ('void',):
				r ='void'
			return r

	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			if this.type.name == 'byte':
				return 'new byte[0]'  # equals to java 
			return 'new List<%s>()'%this.type.getMappingTypeName(call_module)

		@classmethod
		def typeName(cls,this,call_module):
			if this.type.name == 'byte':
				return 'byte[]'
			return 'List<%s>'%this.type.getMappingTypeName(call_module)


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'new Dictionary<%s,%s>()'%(this.first.getMappingTypeName(call_module),
											 this.second.getMappingTypeName(call_module)
											)

		@classmethod
		def typeName(cls,this,call_module):
			return 'Dictionary< %s,%s >'%(this.first.getMappingTypeName(call_module),
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

class Indent:
	def __init__(self):
		self.indents = 0

	def inc(self,n=1):
		self.indents += n

	def dec(self,n=1):
		self.indents -=n
		if self.indents < 0 :
			self.reset()

	def reset(self):
		self.indents = 0

	def str(self):
		return '\t'*self.indents



class StreamWriter:
	def __init__(self,ostream=None,idt=None):
		self.ostream = ostream
		self.idt = Indent()
		self.packages =[] #当前包名称
		self.includes ={}
		self.setIncludes('default',[])
		self.defaultinclude = 'default'
		self.varidx = 0
		self.lastvar =''
		self.pkg_prefix = ''

	def newVariant(self,name):
		self.varidx +=1
		self.lastvar = "%s_%s"%(name,self.varidx)
		return self.lastvar

	def resetVariant(self):
		self.varidx = 0

	def setIncludes(self,name,textlist):
		self.includes[name] = textlist

	def getIncludes(self,name='default'):
		txt =''
		if not self.includes:
			return ''
		return self.includes[name]

	def writeIncludes(self,name='default'):
		texts = self.includes[name]
		for t in texts:
			self.writeln(t)

	def writeln(self,s,*s1):
		self.ostream.write(self.idt.str())
		self.ostream.write( str(s) )
		for s in s1:
			self.ostream.write( str(s))
		self.ostream.write(NEWLINE)
		return self

	def wln(self):
		self.writeln('')
		return self

	def write(self,s,*s1):
		self.ostream.write(self.idt.str())
		self.ostream.write( str(s) )
		for s in s1:
			self.ostream.write( str(s))
		return self

	def idt_inc(self):
		self.idt.inc()
		return self

	def idt_dec(self):
		self.idt.dec()
		return self

	def brace1(self):
		self.ostream.write('{')
		return self

	def brace2(self):
		self.ostream.write('}')
		return self

	def newline(self):
		return self.write('')

	def scope_begin(self):
		return self.newline().brace1().wln().idt_inc()

	def scope_end(self):
		return self.idt_dec().newline().brace2().wln()

	def define_var(self,name,type,val=None):
		txt ="%s %s"%(type,name)
		if val:
			txt+=" = "+ val
		txt+=";"
		self.writeln(txt)

	def createPackage(self,name):

		# if self.pkg_prefix:
		# 	name = os.path.join(self.pkg_prefix,name)

		if not  os.path.exists(name):
			print 'mkdir:',name
			# os.mkdir(name)
			os.makedirs(name)

	#进入包空间
	def pkg_enter(self,name):
		self.packages.append(name)
		# if self.pkg_prefix:
		# 	name = os.path.join(self.pkg_prefix,name)
		os.chdir(name)


	def pkg_current(self):
		import string
		if self.pkg_prefix:
			return self.pkg_prefix + '.' + string.join(self.packages,'.')
		else:
			return string.join(self.packages,'.')

	def pkg_leave(self):
		pkg = self.packages[-1]
		os.chdir('../')

	def pkg_begin(self):
		pkg = self.packages[-1]
		if not pkg:return
#		self.write("package %s"%pkg).brace1().wln().idt_dec()
#		print pkg
		self.idt.reset()

		if self.pkg_prefix:
			self.writeln("package %s;"%(self.pkg_prefix+'.'+pkg) )
		else:
			self.writeln("package %s;"%pkg)

	def pkg_end(self):
		pass
#		self.idt_dec().wln().brace2()

	def classfile_enter(self,name,file=''):
		if file:
			self.ostream = open(file+'.java','w')
		else:
			self.ostream = open(name+'.java','w')
		self.pkg_begin()
		#self.idt_inc()
		self.writeIncludes()
		#self.idt_inc()

	def classfile_leave(self):
		self.idt_dec()
		self.pkg_end()
		self.ostream.close()



class Builtin_Python:
	def __init__(self):
		pass

	'csharp default: LITTLE_ENDIAN '
	@staticmethod
	def serial(typ,val,sw,stream):
		# typ - builtin object ; val - variant name; var = d
		s=''
		if typ.type =='byte':
			# sw.writeln('%s.writeByte(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeByte(%s,%s);'%(val,stream))
		if typ.type =='short':
			# sw.writeln('%s.writeShort(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeShort(%s,%s);;'%(val,stream))
		if typ.type =='int':
			# sw.writeln('%s.writeInt(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeInt(%s,%s);'%(val,stream))
		if typ.type =='long':
			# sw.writeln('%s.writeLong(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeLong(%s,%s);'%(val,stream))
		if typ.type =='float':
			# sw.writeln('%s.writeFloat(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeFloat(%s,%s);'%(val,stream))
		if typ.type =='double':
			# sw.writeln('%s.writeDouble(%s);'%(stream,val))
			sw.writeln('RpcBinarySerializer.writeDouble(%s,%s);'%(val,stream))
		if typ.type =='string':
			# v = sw.newVariant('sb')
			# sw.writeln('byte[] %s = %s.getBytes();'%(v,val))
			# sw.writeln('%s.writeInt(%s.length);'%(stream,v))
			# sw.writeln('%s.write(%s,0,%s.length);'%(stream,v,v))
			sw.writeln('RpcBinarySerializer.writeString(%s,%s)'%(val,stream))
		if typ.type == 'bool':
			# sw.writeln('%s.writeByte( %s.booleanValue()?1:0);'%(stream,val))
			# sw.writeln('RpcBinarySerializer.writeByte(%s?1:0,%s);'%(val,stream))
			sw.writeln('RpcBinarySerializer.writeBool(%s);'%(val,stream))
		return s

	@staticmethod
	def unserial(typ,val,sw,stream):
		s=''

		if typ.type =='byte':
			# sw.writeln('%s = %s.get();'%(val,stream))
			sw.writeln('%s =RpcBinarySerializer.readByte(%s);'%(val,stream))
		if typ.type =='short':
			# sw.writeln('%s = %s.getShort();'%(val,stream))
			sw.writeln('%s = RpcBinarySerializer.readShort(%s);'%(val,stream))
		if typ.type =='int':
			# sw.writeln('%s = %s.getInt();'%(val,stream))
			sw.writeln('%s = RpcBinarySerializer.readInt(%s);'%(val,stream))
		if typ.type =='long':
			# sw.writeln('%s = %s.getLong();'%(val,stream))
			sw.writeln('%s = RpcBinarySerializer.readLong(%s);'%(val,stream))
		if typ.type =='float':
			# sw.writeln('%s = %s.getFloat();'%(val,stream))
			sw.writeln('%s = RpcBinarySerializer.readFloat(%s);'%(val,stream))
		if typ.type =='double':
			# sw.writeln('%s = %s.getDouble();'%(val,stream))
			sw.writeln('%s = RpcBinarySerializer.readDouble(%s);'%(val,stream))
		if typ.type =='string':
			sw.writeln('%s = RpcBinarySerializer.readString(%s);'%(val,stream))
			# v = sw.newVariant('v')
			# sw.writeln('int %s = %s.getInt();'%(v,stream))
			# v2 = sw.newVariant('_sb')
			# sw.writeln('byte[] %s = new byte[%s];'%(v2,v))
			# sw.writeln('%s.get(%s);'%(stream,v2))
			# sw.writeln('%s = new String(%s);'%(val,v2))

		if typ.type == 'bool':
			sw.writeln('%s = RpcBinarySerializer.readBool(%s);'%(val,stream))
			# v = sw.newVariant('v')
			# sw.writeln('byte %s = %s.get();'%(v,stream))
			# sw.writeln('%s = %s==0?false:true;'%(val,v))

		return s

def createCodeStruct(e,sw,idt):
	module = e.container
	sw.wln()
	params=[ ]
	for m in e.list:
		v = m.type.getMappingTypeName(module)
		params.append( (m.name,v) )
	pp =map(lambda x: '%s %s'%(x[1],x[0]),params)
	ps = string.join(pp,',')

	#--  following is useless in csharp.

	# sw.writeln('import %s.*;'%sw.pkg_current())
	# for ref in module.ref_modules.keys():
	# 	if sw.pkg_current()!=ref:
	# 		sw.writeln('import %s;'%ref)
	#
	# sw.writeln('import java.io.*;')
	# sw.writeln('import java.nio.*;')
	# sw.writeln('import java.util.*;')

	# -- end up --

	sw.wln()
	l ='public class %s{'%e.getName()
	sw.writeln(l)
	sw.writeln("// -- STRUCT -- ")
	sw.idt_inc()

	for m in e.list:
		d = m.type.getTypeDefaultValue(module)
		v = m.type.getMappingTypeName(module)

		sw.writeln("public  %s %s = %s;"%(v,m.name,d))

	sw.wln()
	sw.writeln("//constructor def")
	sw.writeln('public %s(){'%(e.getName(),) )
	sw.idt_inc()
	sw.wln().idt_dec()
	sw.newline().brace2().wln()

#	sw.wln()
#	sw.writeln('public int getSize(){').idt_inc()
#	sw.writeln('int size = 0;')
#	for m in e.list:
#		if isinstance(m.type,Builtin):
#			Builtin_Python.size(m.type,'size',sw)
#		elif isinstance(m.type,Sequence) :
#			sw.writeln('size+= %s.getSize() + 4;'%(m.name))
#		elif isinstance(m.type,Dictionary):
#			sw.writeln('size+= %s.get %s.getSize() + 4;'%(m.name))
#		else:
#			sw.writeln('size+=%s.getSize();'%(m.name))
#	sw.writeln('return size;')
#	sw.scope_end() # end function  getSize()

	#定义序列化函数
	sw.wln()
	sw.resetVariant()
	sw.writeln("// function for data serialization")
	# sw.writeln('public boolean marshall(DataOutputStream d){').idt_inc()
	sw.writeln('public bool marshall(BinaryWriter d){').idt_inc()
	sw.writeln('try{').idt_inc()
	for m in e.list:
#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin): # primitive dialect
			Builtin_Python.serial(m.type, m.name,sw,'d')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			impled = False
			if isinstance(m.type,Sequence) :
				if m.type.type.name=='byte':  # sequence<byte> ->
					# sw.writeln('d.writeInt(%s.length);'%(m.name))
					# sw.writeln('d.write(this.%s,0,%s.length);'%(m.name,m.name))
					sw.writeln('RpcBinarySerializer.writeBytes(%s);'%(m.name)) # write byte[]'s length
					impled = True

			if not impled:
				v = sw.newVariant('_b')
				sw.writeln('%shlp %s = new %shlp(this.%s);'%(m.type.name,v,m.type.name,m.name) )
				sw.writeln('%s.marshall(d);'%v)
		else:
			sw.writeln("%s.marshall(d);"% m.name )
	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
	sw.writeln('return false;')
	sw.scope_end() # end catch

	sw.writeln("return true;")
	sw.scope_end() # end function

	sw.wln()

	#unmarshall()
	sw.resetVariant()
	# sw.writeln("public boolean unmarshall(ByteBuffer d){" )
	sw.writeln("public bool unmarshall(BinaryReader d){" )

	sw.idt_inc()
	sw.define_var("r","bool","false")
	sw.writeln( "try{").idt_inc()

	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type,'this.'+m.name,sw,'d')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):

			impled = False
			if isinstance(m.type,Sequence):
				if m.type.type.name == 'byte':
					# size = sw.newVariant('_s')
					# sw.writeln('int %s = d.getInt();'%(size))
					# sw.writeln('this.%s = new byte[%s];'%(m.name,size))
					# sw.writeln('d.get(this.%s);'%m.name)

					sw.writeln('this.%s = RpcBinarySerializer.readBytes(%s);'%(m.name,))
					impled = True
			if not impled:
				v = sw.newVariant('_b')
				sw.define_var(v,"%shlp"%m.type.name,"new %shlp(this.%s)"%(m.type.name,m.name) )
				sw.writeln("r = %s.unmarshall(d);"%v)
				sw.writeln("if(!r){return false;}")
		else:
			sw.writeln('r = this.%s.unmarshall(d);'%m.name )
			sw.writeln("if(!r){return false;}")

	sw.idt_dec()
	sw.writeln('}catch(Exception e){' ).idt_inc()
	sw.writeln('tce.RpcCommunicator.instance().getLogger().error(e.ToString());')
	sw.writeln('r = false;')
	sw.writeln('return r;' )
	sw.scope_end()

	sw.writeln('return true;')
	sw.scope_end().writeln(' // --  end function -- ')	# end function
	sw.wln()

	sw.scope_end() # end class


def createCodeSequence(e,sw,idt):
	module = e.container
	sw.wln()

	# sw.writeln('import %s.*;'%(sw.pkg_current()) )
	# for ref in module.ref_modules.keys():
	# 	if sw.pkg_current()!=ref:
	# 		sw.writeln('import %s;'%ref)
	#
	# sw.writeln('import java.io.*;')
	# sw.writeln('import java.nio.*;')
	# sw.writeln('import java.util.*;')
	# sw.wln()

	# sequence helper class defination
	sw.writeln('public class %shlp{'%e.getName() )
	sw.idt_inc()
	sw.writeln('//# -- sequence helper class --')
#	sw.wln().writeln("public var ds:Array = null;")
	sw.wln()
	sw.writeln("public List<%s> ds = null;"%e.type.getMappingTypeName(module) )
	sw.writeln('public %shlp(List<%s> ds){'%(e.getName(),e.type.getMappingTypeName(module)) ).idt_inc()
	sw.writeln('this.ds = ds;')
	sw.scope_end().wln()


	# sw.writeln('public boolean marshall(DataOutputStream d){').idt_inc()
	sw.writeln('public bool marshall(BinaryWriter d){').idt_inc()
	sw.writeln('try{').idt_inc()
	# sw.writeln("d.writeInt(this.ds.size());")
	sw.writeln('RpcBinarySeriliazer.writeInt(this.ds.Length,d);')
	# sw.writeln('for(%s item : this.ds){'%e.type.getMappingTypeName(module) ).idt_inc()
	sw.writeln('foread(%s item in this.ds){'%e.type.getMappingTypeName(module) ).idt_inc()

	if isinstance( e.type,Builtin):
		Builtin_Python.serial(e.type,'item',sw,'d')
		#数组不能直接存储 原始数据类型 builtin_type
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		impled = False
		if isinstance(e.type,Sequence): # just sequence with parameterized 'byte'
			if e.type.type.name == 'byte':
				# sw.writeln('d.writeInt(item.length);')
				# sw.writeln('d.write(item,0,item.length);')

				sw.writeln('RpcBinarySerializer.writeBytes(item,d);')
				impled = True
		if not impled:
			v = sw.newVariant('_b')
			sw.define_var(v,'%shlp'%e.type.name,'new %shlp(item)'%(e.type.name) )
			sw.writeln('%s.marshall(d);'%v)
	else:
		sw.writeln("item.marshall(d);")

	sw.scope_end()	#end for
	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
	sw.writeln('RpcCommunicator.install().logger.error(e.ToString());')
	sw.writeln('return false;')
	sw.scope_end()

	sw.writeln("return true;")
	sw.scope_end() # end function
	sw.wln()

	#-- function "unmarshall" --

	# sw.writeln('public boolean unmarshall(ByteBuffer d){').idt_inc()
	sw.writeln('public bool unmarshall(BinaryReader d){').idt_inc()
	vsize = sw.newVariant('_size')

	sw.writeln('int %s = 0;'%vsize)

	sw.writeln('try{').idt_inc()
	# sw.writeln('%s = d.getInt();'%vsize)
	sw.writeln('%s = RpcBinarySerializer.readInt(d);'%vsize)
	v_p = sw.newVariant('_p')
	# sw.writeln("for(int _p=0;_p < %s;_p++){"%(vsize)).idt_inc()
	sw.writeln("for(int %s = 0;%s < %s;%s++){"%(v_p,v_p,vsize,v_p)).idt_inc()

	v = sw.newVariant('_b')
	if isinstance(e.type,Builtin): #无法包装直接的原始数据数组
		# sw.define_var("_o",e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
		sw.define_var("%s"%v,e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
		Builtin_Python.unserial(e.type,'%s'%v,sw,'d')
		# sw.writeln("this.ds.add(_o);")
		sw.writeln("this.ds.Add(%s);"%v)

	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):
		impled = False
		if isinstance(e.type,Sequence):
			if e.type.type.name == 'byte':
				# size = sw.newVariant('_s')
				bf = sw.newVariant('_bf')
				# sw.writeln('int %s = d.getInt();'%(size))
				# sw.writeln('byte[] %s = new byte[%s];'%(bf,size))
				# sw.writeln('d.get(%s);'%bf)
				sw.writeln('byte[] %s = RpcBinarySerializer.readBytes(d);'%bf)
				# sw.writeln('this.ds.add(%s);'%bf)
				sw.writeln('this.ds.Add(%s);'%bf)
				impled = True

		if not impled:
			sw.define_var(v,e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
			c = sw.newVariant('_b')
			sw.define_var(c,"%shlp"%e.type.name,"new %shlp(%s)"%(e.type.name,v))
			sw.writeln("%s.unmarshall(d);"%(c))
			# sw.writeln("this.ds.add(%s);"%v)
			sw.writeln("this.ds.Add(%s);"%v)
	else:
		sw.define_var(v,e.type.name,"new %s()"%e.type.name)
		sw.writeln("%s.unmarshall(d);"%v)
		# sw.writeln("this.ds.add(%s);"%v)
		sw.writeln("this.ds.Add(%s);"%v)
	sw.scope_end() # end for{}

	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
	sw.writeln('RpcCommunicator.instance().logger.error(e.ToString());')
	sw.writeln('return false;')
	sw.scope_end()

	sw.writeln("return true;")
	sw.scope_end() # end function

	sw.wln()
	sw.scope_end() # end class sequence
	sw.wln()


def createCodeDictionary(e,sw,idt):
	if True:
		module = e.container

		# sw.wln()
		# sw.writeln('import %s.*;'%(sw.pkg_current()) )
		# for ref in module.ref_modules.keys():
		# 	if sw.pkg_current()!=ref:
		# 		sw.writeln('import %s;'%ref)
		#
		# sw.writeln('import tce.*;')
		# sw.writeln('import java.util.*;')
		# sw.writeln('import java.io.*;')
		# sw.writeln('import java.nio.*;')

		sw.wln()
		sw.writeln('public class %shlp {'%e.getName() ).idt_inc()
		sw.writeln('//-- dictionary --')
	#	sw.writeln('public var ds :HashMap = null;').wln()
		sw.writeln('public %s ds = null;'%(e.getMappingTypeName(module))).wln()
		sw.writeln('public %shlp(%s ds){'%(e.name,e.getMappingTypeName(module)) ).idt_inc()	#将hash数据{}传递进来
		sw.writeln('this.ds = ds;')
		sw.scope_end()
		sw.wln()

		sw.resetVariant()
		# -- FUNCTION marshall()  BEGIN --
		# sw.writeln('public boolean marshall(DataOutputStream d){').idt_inc()
		sw.writeln('public bool marshall(BinaryWriter d){').idt_inc()

		sw.writeln('try{').idt_inc()
		# sw.writeln('d.writeInt(this.ds.size());')

		sw.writeln('RpcBinarySerializer.writeInt(this.ds.Count,d);')

		k = sw.newVariant('_k')
		v = sw.newVariant('_v')
		kv = sw.newVariant('_kv')
		# sw.writeln('for( %s %s : this.ds.keySet()){'%(e.first.getMappingTypeName(module),k )).idt_inc()
		sw.writeln('foreach( KeyValuePair<%s,%s> %s in this.ds ){'%(e.first.getMappingTypeName(module),e.second.getMappingTypeName(module),kv )).idt_inc()

		# sw.define_var(v,e.second.getMappingTypeName(module),'ds.get(%s)'%(k))
		# do key
		if isinstance( e.first,Builtin):
			Builtin_Python.serial(e.first,'%s.Key'%kv,sw,'d')
		elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'error: <KEY> in dictionary not be in [sequence,dictionary]!'
			sys.exit(0)
			#key不支持符合数据类型，只能是简单数据类型(Builtin Types)
			# c = sw.newVariant('_c')
			# sw.define_var(c,'%shlp'%e.first.name,'new %shlp(%s)'%(e.first.name,k) )
			# sw.writeln('%s.marshall(d);'%c)
		else:
			sw.writeln("%s.Key.marshall(d);"%kv)

		# do value (second field)
		if isinstance( e.second,Builtin):
			Builtin_Python.serial(e.second,'%s.Value'%kv,sw,'d')
#			sw.scope_end()
		elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
			impled = False
			if isinstance( e.second,Sequence):
				if e.second.type.name == 'byte':
					# sw.writeln('d.writeInt(%s.length);'%v)
					# sw.writeln('d.write(%s,0,%s.length);'%(v,v))
					sw.writeln('RpcBinarySerializer.writeBytes(%s.Value,d);'%kv)
					impled = True

			if not impled:
				c = sw.newVariant('_c')
				sw.define_var(c,'%shlp'%e.second.name,'new %shlp(%s.Value)'%(e.second.name,kv) )
				sw.writeln('%s.marshall(d);'%c)
		else:
			sw.writeln("%s.marshall(d);"%v)
		sw.scope_end() # end for

		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		sw.writeln('RpcCommunicator.instance().logger.error(e.ToString());')
		sw.writeln('return false;')
		sw.scope_end() # end try{}
		sw.writeln('return true;')
		sw.scope_end() # end function
		sw.wln()


		"""
		dictionary<k,v> 的key必须是 primitive 类型
		"""
		sw.writeln("// dictionay function unmarshall")
		sw.resetVariant()
		# sw.writeln('public boolean unmarshall(ByteBuffer d){').idt_inc()
		sw.writeln('public bool unmarshall(BinaryReader d){').idt_inc()
		vsize = sw.newVariant('_size')
		sw.writeln('int %s = 0;'%vsize)

		sw.writeln('try{').idt_inc()

		# sw.writeln('%s = d.getInt();'%vsize)

		sw.writeln('%s = RpcBinarySerializer.readInt(d);'%vsize)


		v_p = sw.newVariant('_vp')
		sw.writeln("for(int %s = 0; %s < %s; %s++){"%(v_p,v_p,vsize,v_p)).idt_inc()
		k = sw.newVariant('_k')
		v = sw.newVariant('_v')
		c = sw.newVariant('_c')

		sw.define_var(k,e.first.getMappingTypeName(module),e.first.getTypeDefaultValue(module) )
		if isinstance(e.first,Builtin):
			Builtin_Python.unserial(e.first,k,sw,'d')

		elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'error: dictionary<KEY,..> in dictionary cannot be in [ sequence,dictionary ]!'
			sys.exit(0)
			# sw.define_var(c,'%shlp'%e.first.name,'new %shlp(%s)'%(e.first.name,k))
			# sw.writeln('%s.unmarshall(d);'%(c))
		else:
			# sw.writeln('%s.unmarshall(d);'%k)
			print 'error: dictionary<KEY,..>  key must not be structure or complexed object !'
			sys.exit(0)

		c = sw.newVariant('_c')
		sw.define_var(v,e.second.getMappingTypeName(module),e.second.getTypeDefaultValue(module) )
		if isinstance(e.second,Builtin):
			Builtin_Python.unserial(e.second,v,sw,'d')
		elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
			impled = False
			if isinstance(e.second,Sequence):
				if e.second.type.name == 'byte':
					# size = sw.newVariant('_s')
					# bf = sw.newVariant('_bf')
					# sw.writeln('int %s = d.getInt();'%(size))
					# sw.writeln('%s = new byte[%s];'%(v,size))
					# sw.writeln('d.get(%s);'%v)
					sw.writeln('%s = RpcBinarySerializer.readBytes(d);'%v)

					impled = True

			if not impled:
				sw.define_var(c,'%shlp'%e.second.name,'new %shlp(%s)'%(e.second.name,v))
				sw.writeln('%s.unmarshall(d);'%(c))
		else:
			sw.writeln('%s.unmarshall(d);'%v)


		sw.writeln("this.ds.put(%s,%s);"%(k,v))
		sw.scope_end() # end for



		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		sw.writeln('return false;')
		sw.scope_end() # end try{}

		sw.wln()


		sw.writeln('return true;')
		sw.scope_end()	# end function

		sw.scope_end() # end class
		sw.writeln('//-- end Dictonary Class definations --')
		sw.wln()


def createProxy(e,sw,ifidx):
	"""
	创建代理对象
	:param e:   interface
	:param sw: streamwriter
	:param ifidx: interface-index
	:return:
	"""
	# 创建代理
	module = e.container

	# sw.classfile_enter('%sProxy'%e.getName())
	# sw.wln()
	#
	# sw.writeln('import tce.*;')
	# sw.writeln('import java.io.*;')
	# sw.writeln('import java.nio.*;')
	# sw.writeln('import java.util.*;')
	# sw.wln()

	#	sw.writeln("import %s.%s;"%(sw.pkg_current(), e.getName() ) )
	sw.wln()
	sw.writeln('public class %sProxy:RpcProxyBase{'%e.getName() ).idt_inc()
	sw.writeln("//# -- INTERFACE PROXY -- ")
	#
	sw.wln()
	sw.writeln("public %sProxy(RpcConnection conn){"%(e.getName())).idt_inc()
	sw.writeln("this.conn = conn;")
	sw.scope_end().wln()

	#--create()
	sw.writeln('public static %sProxy create(string host,int port,bool ssl_enable){'%e.getName()).idt_inc()
	sw.writeln('int type = RpcConstValue.CONNECTION_SOCK;')
	sw.writeln('if (ssl_enable) type |= RpcConstValue.CONNECTION_SSL;')
	sw.writeln('RpcConnection conn = RpcCommunicator.instance().'
			   'createConnection(type,'
			   'host,port);')


	sw.writeln('%sProxy prx = new %sProxy(conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()

	#--createWithProxy()
	sw.writeln('public static %sProxy createWithProxy(RpcProxyBase proxy){'%e.getName()).idt_inc()
	sw.writeln('%sProxy prx = new %sProxy(proxy.conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()


	#-- end create()
	sw.wln()
	#-- begin destroy()
	sw.writeln('public void destroy(){').idt_inc()
	sw.writeln('try{').idt_inc()
	sw.writeln('conn.close();')
	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
	sw.writeln('RpcCommunicator.instance().getLogger().error(e.ToString());')
	sw.scope_end()
	sw.scope_end()

	#-- end destroy()
	# throws not existed in c# !!!!
	for opidx,m in enumerate(e.list): # function list
		sw.wln()
		#------------BEGIN TOWAY CALL with timeout ----------------------------------------
		params=[]
		#		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象
		list =[]
		for p in m.params:
		#			params.append( p.id,p.type.getMappingTypeName())
			list.append('%s %s'%(p.type.getMappingTypeName(module),p.id) )
		s = string.join( list,',')
		# 函数定义开始


		# sw.writeln('public %s %s(%s) throws RpcException{'%(m.type.getMappingTypeName(module),m.name,s) ).idt_inc()
		sw.writeln('public %s %s(%s){'%(m.type.getMappingTypeName(module),m.name,s) ).idt_inc()
		if m.type.name!='void':
			sw.write('return ')
		_params =[]
		for p in m.params:
			_params.append(p.id)

		_params = string.join(_params,',')
		if _params: _params +=','
		sw.ostream.write('%s(%RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);'%(m.name,_params) )
		sw.wln() #.idt_inc().wln()
		sw.scope_end()

		if s: s = s + ','
		#-- 生成同步函数
		sw.writeln('// timeout - msec ,  0 means waiting infinitely')
		# sw.writeln('public %s %s(%sint timeout,HashMap<String,String> props) throws RpcException{'%(m.type
		sw.writeln('public %s %s(%sint timeout,Dictionary<string,string> props) {'%(m.type
																									.getMappingTypeName(module),
																									m.name,s) ).idt_inc()
		sw.resetVariant()
		r = sw.newVariant('r')
		sw.define_var(r,'bool','false')
		m1 = sw.newVariant('m')
		sw.define_var(m1,'RpcMessage','new RpcMessage(RpcMessage.CALL)')

		sw.writeln("%s.ifidx = %s;"%(m1,ifidx))
		sw.writeln("%s.opidx = %s;"%(m1,opidx))
		sw.writeln('%s.paramsize = %s;'%(m1,len(m.params)))
		sw.writeln('%s.extra.setProperties(props);'%m1)
		sw.writeln('try{').idt_inc()
		if len(m.params):
			bos = sw.newVariant('bos')
			# sw.writeln('ByteArrayOutputStream %s = new ByteArrayOutputStream();'%bos)
			sw.writeln('MemoryStream %s = new MemoryStream();'%bos)
			dos = sw.newVariant('dos')
			# sw.writeln('DataOutputStream %s = new DataOutputStream(%s);'%(dos,bos))
			sw.writeln('BinaryWriter %s = new BinaryWriter(%s);'%(dos,bos))

		for p in m.params:
			if isinstance(p.type,Builtin):
				Builtin_Python.serial(p.type,p.id,sw,dos)
			elif isinstance(p.type,Sequence)  or isinstance(p.type,Dictionary):
				impled = False
				if isinstance(p.type,Sequence):
					if p.type.type.name == 'byte':
						sw.writeln('%s.writeInt(%s.length);'%(dos,p.id))
						sw.writeln('%s.write(%s,0,%s.length);'%(dos,p.id,p.id))
						impled = True


				if not impled:
					v = sw.newVariant('c')
					sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
					sw.writeln('%s.marshall(%s);'%(v,dos))
			else:
				sw.writeln("%s.marshall(%s);"%(p.id,dos))
		if len(m.params):
			sw.writeln('%s.paramstream = %s.toByteArray();'%(m1,bos))
		sw.writeln("%s.prx = this;"%m1)
		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_DATADIRTY,e.toString());')
		sw.scope_end() # end try()
		# 完成参数打包
		sw.writeln('synchronized(%s){'%m1).idt_inc()
		sw.writeln("%s = this.conn.sendMessage(%s);"%(r,m1))
		sw.writeln("if(!%s){"%r).idt_inc()
		sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_SENDFAILED);')
		sw.scope_end() # end if()

		#BEGIN WAITING
		sw.writeln('try{').idt_inc()
		# sw.writeln('synchronized(%s){'%m1).idt_inc()
		sw.writeln('if( timeout > 0) %s.wait(timeout);'%m1)
		sw.writeln('else %s.wait();'%m1)
		# sw.scope_end() # end synchronized()
		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_INTERNAL_EXCEPTION,e.getMessage());')
		sw.scope_end()
		sw.scope_end() # end synchronized()

		#检测错误码
		sw.writeln('if (%s.errcode != RpcConstValue.RPCERROR_SUCC){'%m1).idt_inc()
		sw.writeln('throw new RpcException(%s.errcode);'%m1)
		sw.scope_end()

		sw.writeln('if( %s.result == null){'%m1).idt_inc() #网络断开
		sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_TIMEOUT);') #超时
		sw.scope_end()

		if m.type.name !='void':
		# if True:
			v = sw.newVariant('b')
			sw.define_var(v,m.type.getMappingTypeName(module),m.type.getTypeDefaultValue(module) )
			sw.writeln('try{').idt_inc()
			m2 = sw.newVariant('m2')
			sw.writeln('RpcMessage %s = (RpcMessage) %s.result;'%(m2,m1))
			d = sw.newVariant('d')
			sw.writeln('ByteBuffer %s = ByteBuffer.wrap(%s.paramstream);'%(d,m2))
			#		sw.writeln('try{').idt_inc()

			#返回值必须是 sequence 或者 struct
			if  isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
				impled = False
				if isinstance(m.type,Sequence):
					if m.type.type.name == 'byte':
						size = sw.newVariant('_s')
						sw.writeln('int %s = %s.getInt();'%(size,d))
						sw.writeln('%s = new byte[%s];'%(v,size))
						sw.writeln('%s.get(%s);'%(d,v))
						impled = True

				if not impled:
					c = sw.newVariant('ar')
					sw.define_var(c,'%shlp'%m.type.name,'new %shlp(%s)'%(m.type.name,v))
					sw.writeln('%s = %s.unmarshall(%s);'%(r,c,d))
			elif isinstance(m.type,Struct):
				sw.writeln('%s = %s.unmarshall(%s);'%(r,v,d))
			else:
				Builtin_Python.unserial(m.type,v,sw,d)
			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_DATADIRTY);')
			sw.scope_end()

			sw.writeln('return %s; //regardless if  unmarshalling is okay '%v)

		sw.scope_end() # end function()
		#end rpc proxy::call()  --

		sw.wln()


		#---------- BEGIN ONEWAY CALL ------------------------------------------
		#-----------Just  void return  ONEWAY call -----------------------------------------
		if m.type.name =='void':
			params=[]
			list =[]
			sw.resetVariant()
			for p in m.params:
				list.append('%s %s'%(p.type.getMappingTypeName(module),p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s+','

			sw.writeln('public %s %s_oneway(%sHashMap<String,String> props) throws RpcException{'%(m.type.name,m.name,s) ).idt_inc()
			r = sw.newVariant('r')
			sw.define_var(r,'boolean','false')
			m1 = sw.newVariant('m')
			sw.define_var(m1,'RpcMessage','new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY)')
			sw.writeln("%s.ifidx = %s;"%(m1,ifidx))
			sw.writeln("%s.opidx = %s;"%(m1,opidx))
			sw.writeln('%s.paramsize = %s;'%(m1,len(m.params)))
			sw.writeln('%s.extra.setProperties(props);'%m1)

			sw.writeln('try{').idt_inc()
			if len(m.params):
				bos = sw.newVariant('bos')
				sw.writeln('ByteArrayOutputStream %s = new ByteArrayOutputStream();'%bos)
				dos = sw.newVariant('dos')
				sw.writeln('DataOutputStream %s = new DataOutputStream(%s);'%(dos,bos))

			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.serial(p.type,p.id,sw,dos)
				elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
					impled = False
					if p.type.type.name == 'byte':
						sw.writeln('%s.writeInt(%s.length);'%(dos,p.id))
						sw.writeln('%s.write(%s,0,%s.length);'%(dos,p.id,p.id))
						impled = True
					if not impled:
						v = sw.newVariant('c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('%s.marshall(%s);'%(v,dos))
				else:
					sw.writeln("%s.marshall(%s);"%(p.id,dos))
			if len(m.params):
				sw.writeln('%s.paramstream = %s.toByteArray();'%(m1,bos))
			sw.writeln("%s.prx = this;"%m1)
			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_DATADIRTY,e.toString());')
			sw.scope_end() # end try()

			sw.writeln("%s = this.conn.sendMessage(%s);"%(r,m1))
			sw.writeln("if(!%s){"%r).idt_inc()
			sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_SENDFAILED);')
			sw.scope_end() # end if()
			sw.scope_end() # end function()
			#end rpc proxy::call()  --

			sw.wln()

		#---------- END ONEWAY CALL ------------------------------------------
		#---------- BEGIN ASYNC CALL ------------------------------------------
		#-----------  void return not be supported -----------------------------------------
		#if m.type.name !='void':
		if True: #支持void异步返回
			params=[]
			list =[]
			for p in m.params:
				list.append('%s %s'%(p.type.getMappingTypeName(module),p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s + ','

			list =[]
			for p in m.params:
				list.append(p.id)
			vs = string.join( list,',')
			if vs: vs = vs +','

			sw.writeln('public void %s_async(%s%s_AsyncCallBack async,HashMap<String,String> props) throws RpcException{'%(m.name,s,e.name) ).idt_inc()
			sw.writeln('%s_async(%sasync,props,null);'%(m.name,vs) )
			sw.scope_end() # end function()
			sw.wln()

			sw.writeln('public void %s_async(%s%s_AsyncCallBack async) throws RpcException{'%(m.name,s,e.name) ).idt_inc()
			sw.writeln('%s_async(%sasync,null,null);'%(m.name,vs) )
			sw.scope_end() # end function()
			sw.wln()


			sw.writeln('public void %s_async(%s%s_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{'%(m.name,s,e.name) ).idt_inc()
			r = sw.newVariant('r')
			sw.define_var(r,'boolean','false')
			m1 = sw.newVariant('m')
			sw.define_var(m1,'RpcMessage','new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC)')
			sw.writeln("%s.ifidx = %s;"%(m1,ifidx))
			sw.writeln("%s.opidx = %s;"%(m1,opidx))
			sw.writeln('%s.paramsize = %s;'%(m1,len(m.params)))
			sw.writeln('%s.extra.setProperties(props);'%m1)
			sw.writeln('%s.cookie = cookie;'%m1)
			sw.writeln('try{').idt_inc()
			if len(m.params):
				bos = sw.newVariant('bos')
				dos = sw.newVariant('dos')
				sw.writeln('ByteArrayOutputStream %s = new ByteArrayOutputStream();'%bos)
				sw.writeln('DataOutputStream %s = new DataOutputStream(%s);'%(dos,bos))

			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.serial(p.type,p.id,sw,dos)
				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					impled = False
					if isinstance(p.type,Sequence):
						if p.type.type.name == 'byte':
							sw.writeln('%s.writeInt(%s.length);'%(dos,p.id))
							sw.writeln('%s.write(%s,0,%s.length);'%(dos,p.id,p.id))
							impled = True
					if not impled:
						v = sw.newVariant('c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('%s.marshall(%s);'%(v,dos))
				else:
					sw.writeln("%s.marshall(%s);"%(p.id,dos))
			if m.params:
				sw.writeln('%s.paramstream = %s.toByteArray();'%(m1,bos))
			sw.writeln("%s.prx = this;"%m1)
			sw.writeln('%s.async = async;'%m1)
			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_DATADIRTY,e.toString());')
			sw.scope_end() # end try()

			sw.writeln("%s = this.conn.sendMessage(%s);"%(r,m1))
			sw.writeln("if(!%s){"%r).idt_inc()
			sw.writeln('throw new RpcException(RpcConstValue.RPCERROR_SENDFAILED);')
			sw.scope_end() # end if()
			sw.scope_end() # end function()
			#end rpc proxy::call()  --

			sw.wln()

		#---------- END ASYNC CALL ------------------------------------------
		sw.wln()
	sw.scope_end() # end class PROXY class END --  '}'
	sw.classfile_leave()

	#---------------定义 异步调用 基类  --------------------

	sw.classfile_enter('%s_AsyncCallBack'%(e.getName()))
	sw.wln()

	sw.writeln('import %s.*;'%sw.pkg_current())
	for ref in module.ref_modules.keys():
		if sw.pkg_current()!=ref:
			sw.writeln('import %s;'%ref)
	sw.writeln('import tce.*;')
#	sw.writeln('import java.io.*;')

	sw.writeln('import java.nio.*;')
	sw.writeln('import java.util.*;')
	sw.wln()

	sw.writeln('public class %s_AsyncCallBack extends RpcAsyncCallBackBase{'%(e.getName() )).idt_inc()
	#定义异步回调接收函数

	sw.writeln('// following functions should be ovrrided in user code.')
	for m in e.list: # func
		# if m.type.name =='void': continue
		if m.type.name == 'void':   # void 类型也接受异步回调
			sw.writeln('public void %s(RpcProxyBase proxy,Object cookie){'%(m.name)).idt_inc()
		else:
			sw.writeln('public void %s(%s result,RpcProxyBase proxy,Object cookie){'%(m.name,m.type.getMappingTypeName(module))).idt_inc()
		sw.scope_end()
		sw.wln()

	sw.writeln('@Override')
	sw.writeln('public void callReturn(RpcMessage m1,RpcMessage m2){').idt_inc()
	sw.writeln('boolean r = false;')
	sw.writeln('ByteBuffer d = ByteBuffer.wrap(m2.paramstream);')

	for opidx,m in enumerate(e.list):
		#if m.type.name == 'void':
		#	sw.writeln('%s(%s,%s);'%(m.name,'m1.prx','m1.cookie')) #不考虑unmarshall是否okay
		#	sw.scope_end()
		#	continue

		v = sw.newVariant('b')
		sw.writeln('if(m1.opidx == %s){'%opidx).idt_inc()
		if m.type.name =='void':
			sw.writeln('%s(%s,%s);'%(m.name,'m1.prx','m1.cookie'))
		else:
			sw.define_var(v,m.type.getMappingTypeName(module),m.type.getTypeDefaultValue(module))
			if isinstance(m.type,Builtin):
				Builtin_Python.unserial(m.type,v,sw,'d')
			elif isinstance(m.type,Sequence)  or isinstance(m.type,Dictionary):
	#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())
				impled = False
				if isinstance(m.type,Sequence):
					if m.type.type.name == 'byte':
						size = sw.newVariant('_s')
						sw.writeln('int %s = %s.getInt();'%(size,'d'))
						sw.writeln('%s = new byte[%s];'%(v,size))
						sw.writeln('%s.get(%s);'%('d',v))
						impled = True

				if not impled:
					c = sw.newVariant('c')
					sw.define_var(c,'%shlp'%m.type.name,'new %shlp(%s)'%(m.type.name,v))
					sw.writeln('r = %s.unmarshall(d);'%c)
		#			sw.writeln('%s(%s,%s);'%(m.name,v,'m1.prx')) # 不考虑unmarshall()是否okay

			else:
	#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%m.type.getMappingTypeName())
				sw.writeln('r = %s.unmarshall(d);'%v)
			sw.writeln('%s(%s,%s,%s);'%(m.name,v,'m1.prx','m1.cookie')) #不考虑unmarshall是否okay
		sw.scope_end()
		#		sw.scope_end()

	sw.scope_end() # end funcion callReturn()

	sw.scope_end() # end class  '}'
	sw.classfile_leave()


'''
1.创建 接口类 （服务端dispatch 目标）
2.创建 接口代理类 prx
'''


'''
	interface_defs = {
				{
					func_idx: operatemember
				}
			}
'''
interface_defs={}
ifcnt = 0

def createCodeInterface(e,sw,idt,idx):
	global  interface_defs,ifcnt

	ifidx = ifcnt
	ifcnt+=1

	# ifidx = e.ifidx #过滤之后的接口索引( 暂停 )

	module = e.container    # module is interface's container

		#-------- index of if-cls from extern setting in file
	import tce_util
	ifname = "%s.%s"%(module.name,e.name)
	r = tce_util.getInterfaceIndexWithName(ifname)
	# print 'get if-index:%s with-name:%s'%(r,ifname)
	if r != -1:
		ifidx = r
	#--- end
	e.ifidx = ifidx
	print 'if-index:',ifidx

	interface_defs[ifidx] = {'e':e,'f':{}}

	createProxy(e,sw,ifidx)
	# if not e.delegate_exposed: #是否暴露委托对象,如果需要本地接收远程RPC请求则需要定义filter
	# 	return
	expose = tce_util.isExposeDelegateOfInterfaceWithName(ifname)
	if not expose:
		return
	# begin servant ----
	sw.classfile_enter(e.getName())
	sw.writeln('import tce.*;')

	#接口对象的委托类
	sw.writeln('import %s.%s_delegate;'%(sw.pkg_current(),e.getName()) )
	sw.writeln('import %s.*;'%(sw.pkg_current()) )
	sw.writeln('import java.util.*;')
	for ref in module.ref_modules.keys():
		if sw.pkg_current()!=ref:
			sw.writeln('import %s;'%ref)

	sw.wln()

	sw.writeln('public class %s extends RpcServant{'%e.getName() )
	sw.idt_inc()
	sw.writeln("//# -- INTERFACE -- ")
#	sw.writeln('var delegatecls:Class = %s_delegate'%e.getName())
#	sw.writeln('public %s_delegate delegate = null;'%e.getName() )
	#写入对应的delegate 类对象
	sw.writeln("public %s(){"%e.getName() ).idt_inc()
	sw.writeln('super();')
	sw.writeln('this.delegate = new %s_delegate(this);'%e.getName())
	sw.scope_end().wln() # end construct function

	#定义servant 接口函数
	for m in e.list: # function list
		sw.wln()
		params=[]
		for p in m.params:
			params.append( (p.id,p.type.getMappingTypeName(module)) )
		list =[]
		for v,t in params:
			list.append('%s %s'%(t,v))
		s = string.join( list,',')
		if s: s += ','
		sw.writeln('public %s %s(%sRpcContext ctx){'%(m.type.getMappingTypeName(module),m.name,s ) ).idt_inc()
		#------------定义默认返回函数----------------------

		if isinstance( m.type ,Builtin ):
			if m.type.name =='void':
#				sw.idt_dec().wln()
				sw.scope_end()
				continue
			else:
				sw.writeln("return %s;"%m.type.getTypeDefaultValue(module))
		elif isinstance(m.type,Sequence):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(module) )
#		elif isinstance(m.type,Dictionary):
#			sw.writeln("return %s;"%m.type.getTypeDefaultValue() )
		else:
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(module) )
		sw.scope_end()

	sw.scope_end() # end class
	sw.classfile_leave()
#	sw.pkg_end()
	# end -servant -----

	#begin delegate() ----

	#------- 定义委托对象 ---------------------------
	sw.classfile_enter("%s_delegate"%e.getName())


	sw.writeln('import tce.*;')
	sw.writeln('import java.io.*;')
	sw.writeln('import java.nio.*;')
	sw.writeln('import java.util.*;')

	sw.writeln("import %s.%s;"%(sw.pkg_current(),e.getName()))
	sw.wln()
	#服务对象调用委托

	sw.writeln("public class %s_delegate extends RpcServantDelegate {"%e.getName()).idt_inc()
	sw.wln()

	sw.writeln('%s inst = null;'%(e.getName()))

#	sw.wln()
	#构造函数
#	sw.writeln("public %s_delegate(%s inst,adapter:CommAdapter=null,conn:RpcConnection=null){"%(e.getName(),e.getName() )).idt_inc()
	sw.writeln("public %s_delegate(%s inst){"%(e.getName(),e.getName() )).idt_inc()
	sw.writeln('this.ifidx = %s;'%ifidx)
#	sw.writeln('this.id = ""; ')  #唯一服务类
#	sw.writeln("this.adapter = adapter;")
#	sw.writeln('this.index = "%s";'%e.getName() )  #接口的xml名称注册到adapter
#	for opidx,m in enumerate(e.list): # function list
#		sw.writeln("this.optlist.put(%s,this.%s);"%(opidx,m.name)) #直接保存 twoway 和 oneway 函数入口

	sw.writeln("this.inst = inst;")
	sw.scope_end().wln() # finish construct()

	#实现invoke()接口
	sw.writeln("@Override")
	sw.writeln("public boolean invoke(RpcMessage m){").idt_inc()
#	sw.writeln('boolean r=false;')
#	sw.writeln('RpcMessageXML m = (RpcMessageXML)m_;')
	for opidx,m in enumerate(e.list):
		sw.writeln('if(m.opidx == %s ){'%opidx).idt_inc()
		sw.writeln('return func_%s_delegate(m);'%opidx )
		sw.scope_end()
	sw.writeln('return false;')
	sw.scope_end() # end - invoke()
	sw.wln()

	#开始委托 函数定义
	for opidx,m in enumerate(e.list): # function list
		sw.writeln('// func: %s'%m.name)
		sw.writeln('boolean func_%s_delegate(RpcMessage m){'%(opidx) ).idt_inc()
		params=[ ]
		sw.writeln('boolean r= false;')
		sw.writeln('r = false;')
		if m.params:
			sw.writeln('ByteBuffer d = ByteBuffer.wrap(m.paramstream);')
		for p in m.params:
			if isinstance(p.type,Builtin):
				sw.define_var(p.id,p.type.getMappingTypeName(module))
				Builtin_Python.unserial(p.type,p.id,sw,'d')
			elif isinstance(p.type,Sequence)  or isinstance(p.type,Dictionary):
				impled = False
				#print p.type,p.type.type.name
				if isinstance(p.type,Sequence):
					if p.type.type.name == 'byte':
						size = sw.newVariant('_s')
						sw.writeln('int %s = %s.getInt();'%(size,'d'))
						sw.writeln('byte[] %s = new byte[%s];'%(p.id,size))
						sw.writeln('%s.get(%s);'%('d',p.id))
						impled = True

				if not impled:
					sw.define_var(p.id,p.type.getMappingTypeName(module),'new %s()'%p.type.getMappingTypeName(module))
					c = sw.newVariant('_array')
					sw.define_var(c,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
					sw.writeln('%s.unmarshall(d);'%c)

			else:
				sw.define_var(p.id,p.type.getMappingTypeName(module),'new %s()'%p.type.getMappingTypeName(module))
				sw.writeln('%s.unmarshall(d);'%p.id)

			params.append(p.id)
		#params = map( lambda x: '_p_'+x,params)
		ps = string.join(params,',')

		if ps: ps = ps + ','
		sw.define_var('servant',e.getName(),'(%s)this.inst'%e.getName())
		sw.writeln('RpcContext ctx = new RpcContext();')
		sw.writeln('ctx.msg = m;')
		if isinstance(m.type,Builtin) and m.type.type =='void': # none return value
			sw.writeln("servant.%s(%sctx);"%(m.name,ps) )
		else:
			sw.define_var('cr',m.type.getMappingTypeName(module))
			sw.writeln("cr = servant.%s(%sctx);"%(m.name,ps) )


		sw.writeln("if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){").idt_inc()
		sw.writeln("return true;") #异步调用不返回等待
		sw.scope_end()

		sw.wln()
		#处理返回值
#
		if m.type.name !='void':
			sw.define_var('mr','RpcMessage','new RpcMessage(RpcMessage.RETURN)')
			sw.writeln('mr.sequence = m.sequence;')
			sw.writeln('mr.callmsg = m;')
			sw.writeln('mr.conn = m.conn;')
			sw.writeln('mr.ifidx = m.ifidx;')
			sw.writeln('mr.call_id = m.call_id;')
			sw.writeln('if(m.extra.getProperties().containsKey("__user_id__")){').idt_inc()
			sw.writeln('mr.extra.setPropertyValue("__user_id__",m.extra.getPropertyValue("__user_id__"));')
			sw.scope_end()



	#		sw.writeln("m.sequence = ctx.msg.sequence;") #返回事务号与请求事务号必须一致
	#
			sw.writeln('try{').idt_inc()
			sw.writeln('ByteArrayOutputStream bos = new ByteArrayOutputStream();')
			sw.writeln('DataOutputStream dos = new DataOutputStream(bos);')
#			sw.writeln('String xml="";')
			if isinstance( m.type ,Builtin ) and m.type.name!='void':
				Builtin_Python.serial(m.type,'cr',sw,'dos')
			elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
				impled = False
				if isinstance(m.type,Sequence):
					if m.type.type.name == 'byte':
						sw.writeln('%s.writeInt(%s.length);'%('dos','cr'))
						sw.writeln('%s.write(%s,0,%s.length);'%('dos','cr','cr'))
						impled = True
				if not impled:
					v = sw.newVariant('_c')
					sw.define_var(v,'%shlp'%m.type.name,'new %shlp(cr)'%m.type.name)
					sw.writeln('%s.marshall(dos);'%v)
			else:
				sw.writeln("cr.marshall(dos);")
			sw.writeln('mr.paramsize = 1;')
			sw.writeln('mr.paramstream = bos.toByteArray();')
			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('r = false;')
			sw.writeln('return r;')
			sw.scope_end()

			sw.writeln("r =m.conn.sendMessage(mr);") #发送回去
		sw.writeln("return r;")

		sw.scope_end() # end servant function{}
		sw.wln()
	sw.scope_end() # end class define
	sw.classfile_leave()
#	sw.pkg_end()
	# end delegate()




#	createProxy(e,sw,ifidx)

	return


def createCodeInterfaceMapping():
	global interface_defs # {e,f:{}}
	pass




def createCodeFrame(module,e,idx,sw ):
	idt = Indent()

	txt='''
		using System;
		using Tce;
		using System.Collections.Generic;
		using System.IO;
		using System.Net;

		namespace %s{;
	'''%module.name

	sw.setIncludes('default',(txt,))
	sw.writeIncludes()
	if isinstance(e,Interface):
		#sw.classfile_enter(e.getName())
		createCodeInterface(e,sw,idt,idx)
		#sw.classfile_leave()


#
	if isinstance(e,Sequence):
		if e.type.name == 'byte':
			return
		sw.classfile_enter(e.getName(),'%shlp'%e.getName() )
		createCodeSequence(e,sw,idt)
		sw.classfile_leave()

#		pass
#
	if isinstance(e,Dictionary):
		sw.classfile_enter(e.getName(),'%shlp'%e.getName())
		createCodeDictionary(e,sw,idt)
		sw.classfile_leave()
		pass


	if isinstance(e,Struct):
		sw.classfile_enter(e.getName())
		createCodeStruct(e,sw,idt)
		sw.classfile_leave()
		return

	sw.scope_end()
#
#	createCodeInterfaceMapping() #创建 链接上接收的Rpc消息 根据其ifx编号分派到对应的接口和函数上去

class Outputer:
	def __init__(self):
		self.files = []

	def addHandler(self,h):
		self.files.append(h)
		return self

	def clearHandler(self):
		self.files = []

	def write(self,s):
		s = s.encode('utf8')
		for f in self.files:
			f.write(s)
			f.flush()



def createCodes():
	global  interface_defs,ifcnt

	file = 'idl/main.idl'

	ostream = Outputer()

	argv = sys.argv
	outdir = './output'
	pkgname = ''
	filters=''
	while argv:
		p = argv.pop(0)
		if p == '-o':
			if argv:
				p = argv.pop(0)
				outdir = p

		if p =='-i':
			if argv:
				p = argv.pop(0)
				file = p

		if p =='-if': # 接口起始下标，如多个module文件并存，则同坐此参数区分开
			if argv:
				ifcnt = int(argv.pop(0))

		if p == '-p':
			if argv:
				pkgname = argv.pop(0)

		if p =='-filter':
			if argv:
				filters = argv.pop(0)

	if not os.path.exists(outdir):
		os.mkdir(outdir)

	import tce_util
	tce_util.getInterfaceIndexWithName('')

	idlfiles = file.strip().split(',')
	for file in idlfiles:
		lexparser.curr_idl_path = os.path.dirname(file)
		parse_idlfile(file)

	unit = syntax_result()
	print global_modules_defs

	os.chdir( outdir )
	for module in global_modules:
		name = module.name
		print 'module and refs:',name,module.ref_modules.keys()


		f = open(os.path.join(outdir,name+'.cs'),'w')
		ostream.clearHandler()
		ostream.addHandler(f)
		ostream.write(headtitles)

		sw = StreamWriter(ostream,Indent())

		# sw.pkg_prefix = pkgname.strip()
		# sw.createPackage(name)  # package is namespace
		# sw.pkg_enter(name)

		for idx,e in enumerate(module.list):
			createCodeFrame(module,e,idx,sw)   #开始处理module代码实现
			ostream.write(NEWLINE)

		sw.pkg_leave()

lexparser.language = 'csharp'
lexparser.lang_kws = ['for','foreach' 'using', 'namespace','float',
					  'new', 'class', 'interface', 'public','protected','private','struct','yield',
					  'while', 'do', 'package', 'sealed','abstract','virtual','override',
					  'as','object','using','namesapce',]
lexparser.codecls = LanguageCSharp

"""
sequence<byte> ->  byte[]

"""

'''
tce2csharp.py 生成代码的namespace的处理方式如同cpp处理方式。
每个module范围内的对象结构统一输出到一个cs文件,这不同java的实现方式（必须每个class独立分布，namespace以package来组织)
'''
def usage():
	howto='''
	python tce2csharp.py -unity -i a.idl,b.idl,..  -o ./
		'''
	print howto

if __name__ =='__main__':
	createCodes()

