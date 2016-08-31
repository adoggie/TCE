#--coding:utf-8--

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
# #javascript

# sequence<byte> 对应  ArrayBuffer类型
# proxy.xxx()调用接口名称不能命名为 [ async,error,props,cookie ]
# btoa( ArrayBuffer) base64换行成 string
# atob( sting) >> ArrayBuffer
# dictionary<key，value> 的key必须是 string , 因为hash直接映射到 Object对象

"""
2015.11.9 scott
  1. 支持 requirejs
"""

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

NEWLINE = '\n'

class StreamWriter:
	def __init__(self,ostream=None,idt=None):
		self.ostream = ostream
		self.idt = Indent()
		self.packages =[] #当前包名称
		self.includes ={}
		self.setIncludes('default',[])
		self.defaultinclude = 'deault'
		self.varidx = 0
		self.lastvar =''

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

	def scope_end2(self): # for inner function
		return self.idt_dec().newline().brace2().write(';').wln()

	def define_var(self,name,type,val=None):
		txt ="var %s"%(name)
		if val:
			txt+=" = "+ val
		txt+=";"
		self.writeln(txt)

	def createPackage(self,name):
		pass
#
#		if not  os.path.exists(name):
#			print 'mkdir:',name
#			os.mkdir(name)

	#进入包空间
	def pkg_enter(self,name):
		pass
#		self.packages.append(name)
#		os.chdir(name)


	def pkg_current(self):
		pass
#		import string
#		return string.join(self.packages,'.')

	def pkg_leave(self):
		pass
#		pkg = self.packages[-1]
#		os.chdir('../')

	def pkg_begin(self):
		pass
#		pkg = self.packages[-1]
#		if not pkg:return
#		self.idt.reset()
#		self.write("package %s;"%pkg)

	def pkg_end(self):
		pass
#		self.idt_dec().wln().brace2()

	def classfile_enter(self,name,file=''):
		pass
#		if file:
#			self.ostream = open(file+'.js','w')
#		else:
#			self.ostream = open(name+'.js','w')
#		self.pkg_begin()
#		#self.idt_inc()
#		self.writeIncludes()
#		#self.idt_inc()

	def classfile_leave(self):
		pass
#		self.idt_dec()
#		self.pkg_end()
#		self.ostream.close()



class Builtin_Python:
	def __init__(self):
		pass

	'java default: BIG_ENDIAN '

	@staticmethod
	def getsize(typ,val,sw):
		if typ.type =='byte':
			sw.writeln('size+= 1;')
		if typ.type =='short':
			sw.writeln('size+= 2;')
		if typ.type =='int':
			sw.writeln('size+= 4;')
		if typ.type =='long':
			sw.writeln('size+= 8;')
		if typ.type =='float':
			sw.writeln('size+= 4;')
		if typ.type =='double':
			sw.writeln('size+= 8;')
		if typ.type =='string':
			v = sw.newVariant('_sb')
			sw.writeln('var %s = tce.utf16to8(%s);'%(v,val))
			sw.writeln('size+= 4 + %s.getBytes().length;'%v)
		if typ.type == 'bool':
			sw.writeln('size+= 1;')

	@staticmethod
	def serial(typ,val,sw,stream,offset='pos'):
		# typ - builtin object ; val - variant name; var = d
		# stream that is DataView(ArrayBuffer())
		s=''
		if typ.type =='byte':
			sw.writeln('%s.setUint8(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=1;'%offset)
		if typ.type =='short':
			sw.writeln('%s.setInt16(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=2;'%offset)
		if typ.type =='int':
			sw.writeln('%s.setInt32(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=4;'%offset)
		if typ.type =='long':
			sw.writeln('%s.setFloat64(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=8;'%offset)
		if typ.type =='float':
			sw.writeln('%s.setFloat32(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=4;'%offset)
		if typ.type =='double':
			sw.writeln('%s.setFloat64(%s,%s);'%(stream,offset,val))
			sw.writeln('%s+=8;'%offset)
		if typ.type =='string':
			v = sw.newVariant('_sb')
			sw.writeln('var %s = tce.utf16to8(%s).getBytes();'%(v,val))
			#sw.writeln('var %s = %s.getBytes();'%(v,v))
			sw.writeln('%s.setInt32(%s,%s.length);'%(stream,offset,v))
			sw.writeln('%s+=4;'%offset)
			v2 = sw.newVariant('_sb')
			sw.writeln('var %s = new Uint8Array(%s.buffer);'%(v2,stream))
			sw.writeln('%s.set(%s,%s);'%(v2,v,offset))
			sw.writeln('%s += %s.length;'%(offset,v))
		if typ.type == 'bool':
			sw.writeln('%s.setUint8(%s,%s==true?1:0);'%(stream,offset,val))
			sw.writeln('%s+=1;'%offset)
		return s

	@staticmethod
	def unserial(typ,val,sw,stream,offset='pos'): # stream -> DataView
		s=''

		if typ.type =='byte':
			sw.writeln('%s = %s.getInt8(%s);'%(val,stream,offset))
			sw.writeln('%s+=1;'%offset)
		if typ.type =='short':
			sw.writeln('%s = %s.getInt16(%s);'%(val,stream,offset))
			sw.writeln('%s+=2;'%offset)
		if typ.type =='int':
			sw.writeln('%s = %s.getInt32(%s);'%(val,stream,offset))
			sw.writeln('%s+=4;'%offset)
		if typ.type =='long':
			sw.writeln('%s = %s.getFloat64(%s);'%(val,stream,offset))
			sw.writeln('%s+=8;'%offset)
		if typ.type =='float':
			sw.writeln('%s = %s.getFloat32(%s);'%(val,stream,offset))
			sw.writeln('%s+=4;'%offset)
		if typ.type =='double':
			sw.writeln('%s = %s.getFloat64(%s);'%(val,stream,offset))
			sw.writeln('%s+=8;'%offset)
		if typ.type =='string':
			v = sw.newVariant('_sb')
			sw.writeln('var %s = %s.getUint32(%s);'%(v,stream,offset))
			sw.writeln('%s+=4;'%offset)

			v2 = sw.newVariant('_sb')
			#sw.writeln('var %s = new  Uint8Array(%s.buffer);'%(v2,stream))
			sw.writeln('%s = %s.buffer.slice(%s,%s+%s);'%(val,stream,offset,offset,v))
			sw.writeln('// this var is Uint8Array,should convert to String!!')
			sw.writeln('%s+= %s;'%(offset,v))
#			sw.writeln('%s = new String(%s);'%(val,v2))
			sw.writeln('%s = String.fromCharCode.apply(null, %s.getBytes());'%(val,val))
			sw.writeln('%s = tce.utf8to16(%s);'%(val,val))

		if typ.type == 'bool':
			v = sw.newVariant('_b')
			sw.writeln('var %s = %s.getInt8(%s);'%(v,stream,offset))
			sw.writeln('%s = %s==0?false:true;'%(val,v))
			sw.writeln('%s+=1;'%offset)

		return s


def createCodeStruct(module,e,sw,idt):
	#sw = StreamWriter(ostream,idt)
	sw.wln()
	params=[ ]
	for m in e.list:
#		v = m.type.getTypeDefaultValue()
		v = m.type.getMappingTypeName(module)
		params.append( (m.name,v) )
	pp =map(lambda x: '%s %s'%(x[1],x[0]),params)
	ps = string.join(pp,',')

	sw.wln()

	#类名
	l ='function %s(){'%e.getName()
	sw.writeln(l)
	sw.writeln("// -- STRUCT -- ")
	sw.idt_inc()

	for m in e.list:
		d = m.type.getTypeDefaultValue(module)
		v = m.type.getMappingTypeName(module)

		sw.writeln("this.%s = %s; "%(m.name,d))
	sw.wln()
	sw.writeln('this.getsize = function(){').idt_inc()
	sw.resetVariant()
	sw.writeln('var size =0;')
	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.getsize(m.type, 'this.'+m.name,sw)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			if isinstance(m.type,Sequence) and m.type.type.name =='byte':
				sw.writeln('size+= 4 + this.%s.byteLength; '%m.name)
			else:
				v = sw.newVariant('_b')
				sw.writeln('var %s = new %shlp(this.%s);'%(v,m.type.name,m.name) )
				sw.writeln('size+=%s.getsize();'%v)
		else:
			sw.writeln("size+=this.%s.getsize();"% m.name )
	sw.writeln('return size;')
	sw.scope_end2()


	#定义序列化函数
	sw.wln()
	sw.writeln("// ")
#	sw.writeln('public boolean marshall(DataOutputStream d){').idt_inc()
	sw.writeln('this.marshall = function(view,pos){').idt_inc()
#	sw.writeln('try{').idt_inc()
	sw.resetVariant()
	for m in e.list:

#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			Builtin_Python.serial(m.type, 'this.'+m.name,sw,'view','pos')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			if isinstance(m.type,Sequence) and m.type.type.name == 'byte':
				v = sw.newVariant('_b')
				sw.writeln('view.setUint32(pos,this.%s.byteLength);'%m.name)
				sw.writeln('pos += 4;')
				sw.writeln('var %s = new Uint8Array(view.buffer);'%(v,))
				sw.writeln('%s.set(this.%s,pos);'%(v,m.name) )
				sw.writeln('pos += this.%s.byteLength;'%m.name)

			else:
				v = sw.newVariant('_b')
				sw.writeln('var %s = new %shlp(this.%s);'%(v,m.type.name,m.name) )
				sw.writeln('pos = %s.marshall(view,pos);'%v)
		else:
			sw.writeln("pos= this.%s.marshall(view,pos);"% m.name )
#	sw.idt_dec().writeln('}catch(e){').idt_inc()
#	sw.writeln('return false;')
#	sw.scope_end() # end catch

#	sw.writeln("return true;")
	sw.writeln('return pos;')
	sw.scope_end2() # end function
	sw.wln()

	#unmarshall()

	sw.writeln("this.unmarshall = function(view,pos){" )
	sw.resetVariant()
	sw.idt_inc()
#	sw.define_var("r","boolean","false")
#	sw.writeln( "try{").idt_inc()


	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type,'this.'+m.name,sw,'view','pos')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):

			if isinstance(m.type,Sequence) and m.type.type.name == 'byte':
				v1 = sw.newVariant('_len')

				sw.writeln('var %s = view.getUint32(pos);'%v1)
				sw.writeln('pos+=4;')
				v2 = sw.newVariant('_v')
				sw.writeln('var %s = new Uint8Array(view.buffer,pos,%s)'%(v2,v1))
				sw.writeln('this.%s = %s.buffer.slice(pos,pos+%s);'%(m.name,v2,v1))
				sw.writeln('pos += %s;'%v1)
			else:
				v = sw.newVariant('_b')
				sw.define_var(v,"%shlp"%m.type.name,"new %shlp(this.%s)"%(m.type.name,m.name) )
				sw.writeln("pos = %s.unmarshall(view,pos);"%v)
	#			sw.writeln("if(!r){return false;}")
		else:
			sw.writeln('pos = this.%s.unmarshall(view,pos);'%m.name )
#			sw.writeln("if(!r){return false;}")

#	sw.idt_dec()
#	sw.writeln('}catch(Exception e){' ).idt_inc()
#	sw.writeln('tce.tce.RpcCommunicator.instance().getLogger().error(e.getMessage());')
#	sw.writeln('r = false;')
#	sw.writeln('return r;' )
#	sw.scope_end()
	sw.writeln('return pos;')
#	sw.writeln('return true;')
	sw.scope_end2().writeln(' // --  end function -- ')	# end function
	sw.wln()

	sw.scope_end() # end class
	sw.wln()

def createCodeSequence(e,sw,idt):
	module = e.container
	sw.wln()

	if isinstance(e.type,Builtin) and e.type.name == 'byte': # sequence<byte> 不生成辅助类,直接使用 ArrayBuffer
		return

	sw.writeln('function %shlp(ds){'%e.getName() ).idt_inc()
	sw.writeln('//# -- SEQUENCE --')
	sw.wln()

	sw.writeln("this.ds = ds; // Array()")
#	sw.scope_end().wln()

	#---- begin getsize() -----
	sw.wln()
	sw.writeln('this.getsize = function(){').idt_inc()
	sw.resetVariant()
	sw.writeln('var size =4;')
	#sw.writeln('size = this.ds.length;')
	sw.writeln('for(var p=0;p<this.ds.length;p++){').idt_inc()
	v = sw.newVariant('_bx')
	sw.writeln('var %s =this.ds[p];'%v)
#	for m in e.list:
	if True:
		m = e
		if isinstance(m.type,Builtin):
			Builtin_Python.getsize(m.type, v,sw)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			if isinstance(m.type,Sequence) and m.type.type.name == 'byte':
				sw.writeln('size+= 4 + %s.byteLength; '% v)
			else:
				v2 = sw.newVariant('_b')
				sw.writeln('var %s = new %shlp(%s);'%(v2,m.type.name,v) )
				sw.writeln('size+=%s.getsize();'%v)
		else:
			sw.writeln("size+=%s.getsize();"% v )
	sw.scope_end() #end for

	sw.writeln('return size;')
	sw.scope_end2()
	sw.wln()
	#---- end getsize() -----

	sw.resetVariant()
	sw.writeln('this.marshall = function(view,pos){').idt_inc()
#	sw.writeln('try{').idt_inc()
	sw.writeln("view.setUint32(pos,this.ds.length);")
	sw.writeln('pos+=4;')
	sw.writeln('for(var n=0;n<this.ds.length;n++){').idt_inc()

	if isinstance( e.type,Builtin):
		Builtin_Python.serial(e.type,'this.ds[n]',sw,'view','pos')
		#数组不能直接存储 原始数据类型 builtin_type
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		if isinstance(e.type,Sequence) and  e.type.type.name == 'byte':
			v1 = sw.newVariant('_v')
			sw.writeln('var %s = new Uint8Array(view.buffer);'%(v1,))
			v2 = sw.newVariant('_v')
			sw.writeln('view.setUint32(pos,this.ds[n].byteLength);')
			sw.writeln('pos += 4;')
			sw.writeln('var %s = new Uint8Array(this.ds[n]); // ds[n] is ArrayBuffer'%(v2,))
			sw.writeln('%s.set(%s,pos);'%(v1,v2) )
			sw.writeln('pos += %s.buffer.byteLength;'%v2)
		else:
			v = sw.newVariant('_b')
			sw.define_var(v,'%shlp'%e.type.name,'new %shlp(this.ds[n])'%(e.type.name) )
			sw.writeln('pos = %s.marshall(view,pos);'%v)
	else:
		sw.writeln("pos = this.ds[n].marshall(view,pos);")

	sw.scope_end()	#end for
#	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
#	sw.writeln('return false;')
#	sw.scope_end();

#	sw.writeln("return true;")
	sw.writeln('return pos;')
	sw.scope_end2() # end function
	sw.wln()
	#def unmarshall()

	sw.resetVariant()
	sw.writeln('this.unmarshall = function(view,pos){').idt_inc()
	vsize = sw.newVariant('_size')

#	sw.writeln('int %s = 0;'%vsize)

#	sw.writeln('try{').idt_inc()
	sw.writeln('var %s = view.getUint32(pos);'%vsize)
	sw.writeln('pos+=4;')
	sw.writeln("for(var _p=0;_p < %s;_p++){"%(vsize)).idt_inc()
	v = sw.newVariant('_b')
	if isinstance(e.type,Builtin): #无法包装直接的原始数据数组
		sw.define_var("_o",e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
		Builtin_Python.unserial(e.type,'_o',sw,'view','pos')
		sw.writeln("this.ds.push(_o);")
	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):

		if isinstance(e.type,Sequence) and e.type.type.name == 'byte':
			v1 = sw.newVariant('_len')
			sw.writeln('var %s = view.getUint32(pos);'%v1)
			sw.writeln('pos+=4;')
			v2 = sw.newVariant('_v')
			sw.writeln('var %s = new Uint8Array(view.buffer,pos,%s)'%(v2,v1))
			sw.writeln('this.ds.push( %s.buffer.slice(pos,pos+%s) );'%(v2,v1))
			sw.writeln('pos += %s;'%v1)
		else:
			sw.define_var(v,e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
			c = sw.newVariant('_b')
			sw.define_var(c,"%shlp"%e.type.name,"new %shlp(%s)"%(e.type.name,v))
			sw.writeln("pos=%s.unmarshall(view,pos);"%(c))
			sw.writeln("this.ds.push(%s);"%v)
	else:
		sw.define_var(v,e.type.name,"new %s()"%e.type.name)
		sw.writeln("pos=%s.unmarshall(view,pos);"%v)
		sw.writeln("this.ds.push(%s);"%v)
	sw.scope_end() # end for{}

#	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
#	sw.writeln('return false;')
#	sw.scope_end()

	sw.writeln("return pos;")
	sw.scope_end2() # end function

	sw.wln()
	sw.scope_end() # end class sequence
	sw.wln()


def createCodeDictionary(e,sw,idt):
		sw.wln()
		module = e.container
		sw.writeln('function %shlp(ds){'%e.getName() ).idt_inc()
		sw.writeln('//# -- THIS IS DICTIONARY! --')
		sw.writeln('this.ds = ds;')
		sw.wln()

		#---- begin getsize() -----
		sw.wln()
		sw.writeln('this.getsize = function(){').idt_inc()
		sw.writeln('var size =4;')

		k = sw.newVariant('_k')
		v = sw.newVariant('_v')
		#sw.writeln('size += Object.getOwnPropertyNames(this.ds).length;')
		# sw.writeln('for( %s in Object.getOwnPropertyNames(this.ds)){'%k).idt_inc()
		sw.writeln('for(var %s in this.ds){'%k).idt_inc()
		sw.define_var(v,e.second.getMappingTypeName(module),'this.ds[%s]'%(k))
		# do key
		# key 应该只允许 Builtin 数据类型,否则停止处理
		if isinstance( e.first,Builtin):
			# if e.first.name !='string':
			# 	print 'error: dictionary:[%s] <key> must be string, current is:[%s]'%(e.name,e.first.name)
			Builtin_Python.getsize(e.first,k,sw)
		elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'warning: %s<key,> is not Builtin type'%e.first.name
			sys.exit()
			c = sw.newVariant('_c')
			sw.define_var(c,'%shlp'%e.first.name,'new %shlp(%s)'%(e.first.name,k) )
			sw.writeln('size+=%s.getsize();'%c)
		else:
			print 'warning: %s<key,> is not Builtin type'%e.first.name
			sys.exit()
			sw.writeln("size+=%s.getsize();"%k)

		# do value
		if isinstance( e.second,Builtin):
			Builtin_Python.getsize(e.second,v,sw)
		#			sw.scope_end()
		elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
			if isinstance(e.second,Sequence) and e.second.type.name=='byte':
				sw.writeln('size+= 4;')
				sw.writeln('if(%s) size += %s.byteLength;'%(v,v))
				# sw.writeln('size+= 4 + %s.byteLength; '%e.second.name)
			else:
				c = sw.newVariant('_c')
				sw.define_var(c,'%shlp'%e.second.name,'new %shlp(%s)'%(e.second.name,v) )
				sw.writeln('size+=%s.getsize();'%c)
		else:
			sw.writeln("size+=%s.marshall();"%v)
		sw.scope_end() # end for

		sw.writeln('return size;')
		sw.scope_end2()
		sw.wln()
		#---- end getsize() -----

		# -- FUNCTION marshall()  BEGIN --
		sw.resetVariant()
		sw.writeln('this.marshall = function(view,pos){').idt_inc()

#		sw.writeln('try{').idt_inc()
		sw.writeln('view.setUint32(pos,Object.keys(this.ds).length);')
		sw.writeln('pos+=4;')

		k = sw.newVariant('_k')
		v = sw.newVariant('_v')
		# sw.writeln('for( %s in Object.getOwnPropertyNames(this.ds)){'%k).idt_inc()
		sw.writeln('for( var %s in this.ds){'%k).idt_inc()
		sw.define_var(v,e.second.getMappingTypeName(module),'this.ds[%s]'%(k,))
		# do key
		if isinstance( e.first,Builtin):
			Builtin_Python.serial(e.first,k,sw,'view','pos')
		elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'warning: %s<key,> is not Builtin type'%e.first.name
			sys.exit()

			c = sw.newVariant('_c')
			sw.define_var(c,'%shlp'%e.first.name,'new %shlp(%s)'%(e.first.name,k) )
			sw.writeln('pos=%s.marshall(view,pos);'%c)
		else:
			print 'warning: %s<key,> is not Builtin type'%e.first.name
			sys.exit()
			sw.writeln("pos=%s.marshall(view,pos);"%k)

		# do value
		if isinstance( e.second,Builtin):
			Builtin_Python.serial(e.second,v,sw,'view','pos')
#			sw.scope_end()
		elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
			if isinstance(e.second,Sequence) and e.second.type.name =='byte':
				sw.writeln('view.setUint32(pos,%s.byteLength);'%v)
				sw.writeln('pos += 4;')
				v1 = sw.newVariant('_v')
				sw.writeln('var %s = new Uint8Array(view.buffer);'%(v1,))
				v2 = sw.newVariant('_v')
				sw.writeln('var %s = new Uint8Array(%s); // ds[n] is ArrayBuffer'%(v2,v))
				sw.writeln('%s.set(%s,pos);'%(v1,v2) )
				sw.writeln('pos += %s.buffer.byteLength;'%v2)
			else:
				c = sw.newVariant('_c')
				sw.define_var(c,'%shlp'%e.second.name,'new %shlp(%s)'%(e.second.name,v) )
				sw.writeln('pos=%s.marshall(view,pos);'%c)
		else:
			sw.writeln("pos=%s.marshall(view,pos);"%v)
		sw.scope_end() # end for

#		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
#		sw.writeln('return false;')
#		sw.scope_end() # end try{}
#		sw.writeln('return true;')
		sw.writeln('return pos;')
		sw.scope_end() # end function
		sw.wln()

		#--	 FUNCTION  unmarshall() BEGIN --
		sw.writeln("// unmarshall()")
		sw.resetVariant()
		sw.writeln('this.unmarshall = function(view,pos){').idt_inc()
		vsize = sw.newVariant('_size')
		sw.writeln('var %s = 0;'%vsize)

#		sw.writeln('try{').idt_inc()
		sw.writeln('%s = view.getInt32(pos);'%vsize)
		sw.writeln('pos+=4;')
	#	sw.writeln("var r:Boolean = false;")
	#	sw.writeln("try{").idt_inc()
	#	sw.define_var("_size","uint","0")
	#	sw.writeln("_size = d.readUnsignedInt();")

		sw.writeln("for(var _p=0;_p < %s;_p++){"%vsize).idt_inc()
		k = sw.newVariant('_k')
		v = sw.newVariant('_v')
		c = sw.newVariant('_c')
		sw.define_var(k,e.first.getMappingTypeName(module),e.first.getTypeDefaultValue(module) )
		if isinstance(e.first,Builtin):
			Builtin_Python.unserial(e.first,k,sw,'view','pos')
		elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'error: dictionary:[%s] key must be Builtin type.'%e.name
			sys.exit()
			sw.define_var(c,'%shlp'%e.first.name,'new %shlp(%s)'%(e.first.name,k))
			sw.writeln('pos=%s.unmarshall(view,pos);'%(c))
		else:
			print 'error: dictionary:[%s] key must be Builtin type.'%e.name
			sys.exit()
			sw.writeln('pos=%s.unmarshall(view,pos);'%k)

		c = sw.newVariant('_c')
		sw.define_var(v,e.second.getMappingTypeName(module),e.second.getTypeDefaultValue(module) )
		if isinstance(e.second,Builtin):
			Builtin_Python.unserial(e.second,v,sw,'view','pos')
		elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
			if isinstance(e.second,Sequence) and e.second.type.name == 'byte':
				v1 = sw.newVariant('_len')
				sw.writeln('var %s = view.getUint32(pos);'%v1)
				sw.writeln('pos += 4;')
				v2 = sw.newVariant('_v')
				sw.writeln('var %s = new Uint8Array(view.buffer,pos,%s);'%(v2,v1))
				sw.writeln('%s = %s.buffer.slice(pos,pos+%s);'%(v,v2,v1))
				# sw.writeln('this.ds.push( %s.buffer );'%(v2,))
				sw.writeln('pos += %s;'%v1)
			else:
				sw.define_var(c,'%shlp'%e.second.name,'new %shlp(%s)'%(e.second.name,v))
				sw.writeln('pos= %s.unmarshall(view,pos);'%(c))
		else:
			sw.writeln('pos=%s.unmarshall(view,pos);'%v)

		sw.writeln("this.ds[%s]=%s;"%(k,v))
		sw.scope_end() # end for

#		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
#		sw.writeln('return false;')
#		sw.scope_end() # end try{}
#
#		sw.wln()
		sw.writeln('return pos;')
		sw.scope_end()	# end function

		sw.scope_end() # end class
		sw.writeln('//-- end Dictonary Class definations --')
		sw.wln()


def createProxy(e,sw,ifidx):
	# 创建代理
#	sw.classfile_enter('%sProxy'%e.getName())
#	sw.writeln("//# -- INTERFACE PROXY -- ")
	#
	sw.wln()
	module = e.container
	sw.writeln("function %sProxy(){"%(e.getName())).idt_inc()
	sw.writeln("this.conn = null;")
	sw.writeln('this.delta =null;')



	sw.wln()
	#-- begin destroy()
	sw.writeln('this.destroy = function(){').idt_inc()
	sw.writeln('try{').idt_inc()
	sw.writeln('this.conn.close();')
	sw.idt_dec().writeln('}catch(e){').idt_inc()
	sw.writeln('tce.RpcCommunicator.instance().getLogger().error(e.toString());')
	sw.scope_end()
	sw.scope_end2()

	#-- end destroy()

	for opidx,m in enumerate(e.list): # function list
		opidx = m.index

		sw.wln()
		#------------BEGIN TOWAY CALL with timeout ----------------------------------------
		params=[]
		#		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象
		list =[]
		for p in m.params:
		#			params.append( p.id,p.type.getMappingTypeName())
			list.append('%s'%(p.id) )
		s = string.join( list,',')
		# 函数定义开始
		if s: s = s + ','

		#---------- BEGIN ONEWAY CALL ------------------------------------------
		#-----------Just  void return  ONEWAY call -----------------------------------------
		if m.type.name =='void':
			params=[]
			list =[]
			for p in m.params:
				list.append('%s'%(p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s+','

			#sw.writeln('//public %s %s_oneway(%sHashMap<String,String> props) throws tce.RpcException{'%(m.type.name,m.name,s) ).idt_inc()
			sw.writeln('this.%s_oneway = function (%serror,props){'%(m.name,s) ).idt_inc()
			sw.define_var('r','boolean','false')
			sw.define_var('m','tce.RpcMessage','new tce.RpcMessage(tce.RpcMessage.CALL|tce.RpcMessage.ONEWAY)')
			sw.writeln("m.ifidx = %s;"%ifidx)
			sw.writeln("m.opidx = %s;"%opidx)
			sw.writeln('m.paramsize = %s;'%len(m.params))
			argc = len(m.params)
			sw.writeln('error = arguments[%s]?arguments[%s]:null;'%( argc,argc))
			sw.writeln('m.onerror = error;')
			sw.writeln('props = arguments[%s]?arguments[%s]:null;'%(argc+1,argc+1))
			sw.writeln('m.extra=props;')

			sw.writeln('try{').idt_inc()
			if len(m.params):
				pass

			sw.writeln('var size =0;')
			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.getsize(p.type,p.id,sw)
				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name == 'byte':
						sw.writeln('size += 4 + %s.byteLength;'%(p.id,))
					else:
						v = sw.newVariant('_c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('size+=%s.getsize();'%v)
				else:
					sw.writeln("size+=%s.getsize();"%p.id)

			buf = sw.newVariant('_bf')
			sw.writeln('var %s = new ArrayBuffer(size);'%buf)
			sw.writeln('var _view = new DataView(%s);'%buf)
			sw.writeln('var _pos=0;')
			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.serial(p.type,p.id,sw,'_view','_pos')
				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name == 'byte':
						v = sw.newVariant('_b')
						sw.writeln('_view.setUint32(_pos,%s.byteLength);'%p.id)
						sw.writeln('_pos += 4;')
						sw.writeln('var %s = new Uint8Array(_view.buffer);'%(v,))
						sw.writeln('%s.set(%s,_pos);'%(v,p.id) )
						sw.writeln('_pos += %s.byteLength;'%p.id)
					else:
						v = sw.newVariant('_c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('_pos = %s.marshall(_view,_pos);'%v)
				else:
					sw.writeln("_pos = %s.marshall(_view,_pos);"%p.id)
			if len(m.params):
				sw.writeln('m.paramstream =%s;'%buf)

			sw.writeln("m.prx = this;")
			sw.idt_dec().writeln('}catch(e){').idt_inc()
#			sw.writeln('throw new tce.RpcException(tce.RpcConsts.RPCERROR_DATADIRTY,e.toString());')
			sw.writeln('console.log(e.toString());')
			sw.writeln('throw "RPCERROR_DATADIRTY";')
			sw.scope_end() # end try()

			sw.writeln("r = this.conn.sendMessage(m);")
			sw.writeln("if(!r){").idt_inc()
			sw.writeln('throw "RPCERROR_SENDFAILED";')
			sw.scope_end() # end if()
			sw.scope_end2() # end function()
			#end rpc proxy::call()  --
#			sw.writeln(';')
			sw.wln()

		#---------- END ONEWAY CALL ------------------------------------------

		#---------- 任何接口函数都有异步返回和单向调用接口 ------------------------------------------
		#if m.type.name !='void':
		if True:
			params=[]

			list =[]
			for p in m.params:
				list.append('%s'%(p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s + ','

			sw.resetVariant()
			sw.writeln('this.%s_async = function(%sasync,error,props,cookie){'%(m.name,s) ).idt_inc()
			sw.define_var('r','boolean','false')
			sw.define_var('m','tce.RpcMessage','new tce.RpcMessage(tce.RpcMessage.CALL|tce.RpcMessage.ASYNC)')
			sw.writeln("m.ifidx		= %s;"%ifidx)
			sw.writeln("m.opidx		= %s;"%opidx)
			argc = len(m.params)
			sw.writeln('error		= arguments[%s]?arguments[%s]:null;'%( argc+1,argc+1))
			sw.writeln('m.onerror	= error;')
			sw.writeln('props		= arguments[%s]?arguments[%s]:null;'%(argc+2,argc+2))
			sw.writeln('m.extra		= props;')
			sw.writeln('cookie 		= arguments[%s]?arguments[%s]:null;'%(argc+3,argc+3))
			sw.writeln('m.cookie	= cookie;')
			sw.writeln('m.extra		= props;')

			sw.writeln('m.paramsize = %s;'%len(m.params))
			sw.writeln('try{').idt_inc()
			if len(m.params):
				pass
			sw.writeln('var size =0;')
			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.getsize(p.type,p.id,sw)
				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name == 'byte':
						sw.writeln('size += 4 + %s.byteLength;'%(p.id,))
					else:
						v = sw.newVariant('_c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('size += %s.getsize();'%v)
				else:
					sw.writeln("size += %s.getsize();"%p.id)

			buf = sw.newVariant('_bf')
			sw.writeln('var %s = new ArrayBuffer(size);'%buf)
			sw.writeln('var _view = new DataView(%s);'%buf)
			sw.writeln('var _pos=0;')
			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.serial(p.type,p.id,sw,'_view','_pos')
				elif isinstance(p.type,Sequence)  or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name == 'byte':
						v = sw.newVariant('_b')
						sw.writeln('_view.setUint32(_pos,%s.byteLength);'%p.id)
						sw.writeln('_pos += 4;')
						sw.writeln('var %s = new Uint8Array(_view.buffer);'%(v,))
						sw.writeln('%s.set(%s,_pos);'%(v,p.id) )
						sw.writeln('_pos += %s.byteLength;'%p.id)
					else:
						v = sw.newVariant('_c')
						sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
						sw.writeln('_pos+=%s.marshall(_view,_pos);'%v)
				else:
					sw.writeln("_pos+=%s.marshall(_view,_pos);"%p.id)
			if len(m.params):
				sw.writeln('m.paramstream =%s;'%buf)

			sw.writeln("m.prx = this;")
			sw.writeln('m.async = async;')
			sw.idt_dec().writeln('}catch(e){').idt_inc()
			sw.writeln('console.log(e.toString());')
			sw.writeln('throw "RPCERROR_DATADIRTY";')
			sw.scope_end() # end try()

			sw.writeln("r = this.conn.sendMessage(m);")
			sw.writeln("if(!r){").idt_inc()
			sw.writeln('throw "tce.RpcConsts.RPCERROR_SENDFAILED";')
			sw.scope_end() # end if()
			sw.scope_end2() # end function()
			#end rpc proxy::call()  --
#			sw.writeln(';')
			sw.wln()

		#---------- END ASYNC CALL ------------------------------------------


	##------------- ASYNC BACK -------------
	sw.wln()


	sw.writeln('this.AsyncCallBack = function(m1,m2){').idt_inc()
#		#定义异步回调接收函数
#		for m in e.list: # func
#			if m.type.name =='void': continue
#			sw.writeln('public void %s(%s result,tce.RpcProxyBase proxy){'%(m.name,m.type.getMappingTypeName())).idt_inc()
#			sw.scope_end()
#			sw.wln()


#		sw.writeln('boolean r = false;')
#		sw.writeln('ByteBuffer d = ByteBuffer.wrap(m2.paramstream);')

	sw.writeln('var array = new Uint8Array(m2.paramstream);')
	sw.writeln('var view = new DataView(array.buffer);')
	sw.writeln('var pos=0;')
	for opidx,m in enumerate(e.list):
		opidx = m.index
		# void 函数接口也支持 async 回调
		# if m.type.name == 'void': continue

		v = sw.newVariant('_b')
		sw.writeln('if(m1.opidx == %s){'%opidx).idt_inc()

		if m.type.name =='void':
			sw.writeln('m1.async(m1.prx,m1.cookie);')
		else:
			sw.define_var(v,m.type.getMappingTypeName(module),m.type.getTypeDefaultValue(module))

			if isinstance(m.type,Builtin):
				Builtin_Python.unserial(m.type,v,sw,'view','pos')
			elif isinstance(m.type,Sequence)  or isinstance(m.type,Dictionary):
			#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())
				if isinstance(m.type,Sequence) and m.type.type.name == 'byte':
					v1 = sw.newVariant('_len')
					sw.writeln('var %s = view.getUint32(pos);'%v1)
					sw.writeln('pos+=4;')
					v2 = sw.newVariant('_v')
					sw.writeln('var %s = new Uint8Array(view.buffer,pos,%s)'%(v2,v1))
					sw.writeln('%s = %s.buffer.slice(pos,pos+%s);'%(v,v2,v1))
					# sw.writeln('pos += %s;'%v1)
				else:
					c = sw.newVariant('_container')
					sw.define_var(c,'%shlp'%m.type.name,'new %shlp(%s)'%(m.type.name,v))
					sw.writeln('pos = %s.unmarshall(view,pos);'%c)
			#			sw.writeln('%s(%s,%s);'%(m.name,v,'m1.prx')) # 不考虑unmarshall()是否okay
			else:
			#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%m.type.getMappingTypeName())
				sw.writeln('pos +=%s.unmarshall(view,pos);'%v)
			sw.writeln('m1.async(%s,m1.prx,m1.cookie);'%v) #不考虑unmarshall是否okay
		# sw.writeln('return;')
		sw.scope_end()

	#		sw.scope_end()

	sw.scope_end2() # end funcion callReturn()

#		sw.scope_end() # end class  '}'
	##------------- ASYNC BACK END -------------
	#sw.writeln(';')
	sw.wln()
	#end AsyncCallBack()

	sw.scope_end() # end class PROXY class END --  '}'
	sw.classfile_leave()

	#---------------静态创建函数  --------------------
	sw.writeln("%sProxy.create = function(uri){"%e.getName()).idt_inc()
	sw.writeln('var prx = new %sProxy();'%e.getName())
	sw.writeln('prx.conn = new tce.RpcConnection(uri);')
	sw.writeln('return prx;')
	sw.scope_end2()
	sw.wln()
	sw.writeln("%sProxy.createWithProxy = function(proxy){"%e.getName()).idt_inc()
	sw.writeln('var prx = new %sProxy();'%e.getName())
	sw.writeln("prx.conn = proxy.conn;")
	sw.writeln('return prx;')
	sw.scope_end2()
	sw.wln()


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

fileifx = open('ifxdef.txt','w') #接口表文件

def createCodeInterface(e,sw,idt,idx):
	global  interface_defs,ifcnt
#	ifidx = ifcnt
#	ifcnt+=1
	print '..createCodeInterface():',e.name
	module = e.container
	# ifidx = e.ifidx
	ifidx = ifcnt
	ifcnt+=1

	# interface_defs[ifidx] = {'e':e,'f':{}}
#	sw.classfile_enter(e.getName())
#	sw.writeln('import tce.*;')



	import tce_util
	ifname = "%s.%s"%(module.name,e.name)
	r = tce_util.getInterfaceIndexWithName(ifname)
	# print 'get if-index:%s with-name:%s'%(r,ifname)
	if r != -1:
		ifidx = r

	e.ifidx = ifidx
	interface_defs[ifidx] = {'e':e,'f':{}}
	fileifx.write('<if id="%s" name="%s.%s"/>\n'%(ifidx,module.name,e.name))
	fileifx.flush()

	tce_util.rebuildFunctionIndex(e)
#
#	#接口对象的委托类
	createProxy(e,sw,ifidx)

	r = tce_util.isExposeDelegateOfInterfaceWithName(ifname)
	e.delegate_exposed = r
	if not e.delegate_exposed:
		print 'delegate not exposed..'
		return

	sw.wln()
	sw.writeln('// class %s'%e.getName())
	sw.writeln('function %s(){'%e.getName() ).idt_inc()
	sw.writeln("//# -- INTERFACE -- ")

	sw.writeln('this.delegate = new %s_delegate(this);'%e.getName())
#	sw.scope_end().wln() # end construct function

	#定义servant 接口函数
	for m in e.list: # function list
		sw.wln()
		params=[]
		for p in m.params:
			params.append( (p.id,p.type.getMappingTypeName(module)) )
		list =[]
		for v,t in params:
			list.append('%s'%(v))
		s = string.join( list,',')
		if s: s += ','
		sw.writeln('//public %s %s(%stce.RpcContext ctx){'%(m.type.getMappingTypeName(module),m.name,s ) )
		sw.writeln('this.%s = function(%sctx){'%(m.name,s ) ).idt_inc()
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
		sw.scope_end2()

	sw.scope_end() # end class


#	sw.classfile_leave()

#	sw.pkg_end()

	#------- 定义委托对象 ---------------------------

	sw.wln()
	#服务对象调用委托
	sw.writeln("function %s_delegate(inst) {"%e.getName()).idt_inc()
	sw.wln()
	sw.writeln('this.inst = inst;')
	sw.writeln('this.ifidx = %s;'%ifidx)
#	sw.wln()
	#构造函数
#	sw.writeln("public %s_delegate(%s inst,adapter:CommAdapter=null,conn:tce.RpcConnection=null){"%(e.getName(),e.getName() )).idt_inc()
#	sw.writeln("public %s_delegate(%s inst){"%(e.getName(),e.getName() )).idt_inc()
#	sw.writeln('this.ifidx = %s;'%ifidx)
#	sw.writeln('this.id = ""; ')  #唯一服务类
#	sw.writeln("this.adapter = adapter;")
#	sw.writeln('this.index = "%s";'%e.getName() )  #接口的xml名称注册到adapter
#	for opidx,m in enumerate(e.list): # function list
#		sw.writeln("this.optlist.put(%s,this.%s);"%(opidx,m.name)) #直接保存 twoway 和 oneway 函数入口

#	sw.writeln("this.inst = inst;")
#	sw.scope_end().wln() # finish construct()

	#实现invoke()接口
#	sw.writeln("@Override")
	sw.writeln("this.invoke = function(m){").idt_inc()
#	sw.writeln('boolean r=false;')
#	sw.writeln('tce.RpcMessageXML m = (tce.RpcMessageXML)m_;')
	for opidx,m in enumerate(e.list):
		opidx = m.index

		sw.writeln('if(m.opidx == %s ){'%opidx).idt_inc()
		sw.writeln('return this.func_%s_delegate(m);'%opidx )
		sw.scope_end()
	sw.writeln('return false;')
	sw.scope_end2() # end - invoke()
	sw.wln()

	#开始委托 函数定义
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.writeln('this.func_%s_delegate = function(m){'%(opidx) ).idt_inc()
		params=[ ]
		sw.writeln('var r = false;')
		sw.writeln('var pos =0;')
		sw.writeln('var array = null;')
		sw.writeln('var view = null;')
#		sw.writeln('r = false;')
		if m.params:
			sw.writeln('array = new Uint8Array(m.paramstream);')
			sw.writeln('view = new DataView(array.buffer);')
		for p in m.params:
			if isinstance(p.type,Builtin):
				sw.define_var(p.id,p.type.getMappingTypeName(module))
				Builtin_Python.unserial(p.type,p.id,sw,'view','pos')
			elif isinstance(p.type,Sequence)  or isinstance(p.type,Dictionary):
				# sw.define_var(p.id,p.type.getMappingTypeName(module),'new %s()'%p.type.getMappingTypeName(module))

				if isinstance(p.type,Sequence) and p.type.type.name == 'byte':
					# sw.define_var(p.id,p.type.getMappingTypeName(module),p.type.getTypeDefaultValue(module))
					sw.writeln('var %s = null;'%p.id)
					v1 = sw.newVariant('_len')
					sw.writeln('var %s = view.getUint32(pos);'%v1)
					sw.writeln('pos+=4;')
					v2 = sw.newVariant('_v')
					sw.writeln('var %s = new Uint8Array(view.buffer,pos,%s)'%(v2,v1))
					sw.writeln('%s = %s.buffer.slice(pos,pos+%s);'%(p.id,v2,v1))
					sw.writeln('pos += %s;'%v1)
				else:
					sw.define_var(p.id,p.type.getMappingTypeName(module),p.type.getTypeDefaultValue(module))
					c = sw.newVariant('_array')
					sw.define_var(c,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
					sw.writeln('pos=%s.unmarshall(view,pos);'%c)
			else:
				sw.define_var(p.id,p.type.getMappingTypeName(module),'new %s()'%p.type.getMappingTypeName(module))
				sw.writeln('pos= %s.unmarshall(view,pos);'%p.id)

			params.append(p.id)
		#params = map( lambda x: '_p_'+x,params)
		ps = string.join(params,',')

		if ps: ps = ps + ','
		sw.define_var('servant',e.getName(),'this.inst')
		sw.writeln('var ctx = new tce.RpcContext();')
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
			sw.define_var('mr','tce.RpcMessage','new tce.RpcMessage(tce.RpcMessage.RETURN)')
			sw.writeln('mr.sequence = m.sequence;')
			sw.writeln('mr.callmsg = m;')
	#		sw.writeln("m.sequence = ctx.msg.sequence;") #返回事务号与请求事务号必须一致
	#
			sw.writeln('try{').idt_inc()
#			sw.writeln('ByteArrayOutputStream bos = new ByteArrayOutputStream();')
#			sw.writeln('DataOutputStream dos = new DataOutputStream(bos);')
#			sw.writeln('String xml="";')
			sw.writeln('var size = 0;')
			sw.writeln('pos=0;')
			if isinstance( m.type ,Builtin ) and m.type.name!='void':
				Builtin_Python.getsize(m.type,'cr',sw)
				sw.writeln('array = new ArrayBuffer(size);')
				sw.writeln('view = new DataView(array);')
				Builtin_Python.serial(m.type,'cr',sw,'view','pos')
			elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
				if isinstance(m.type,Sequence) and m.type.type.name == 'byte':
					sw.writeln('size += 4 + cr.byteLength;')
					sw.writeln('array = new ArrayBuffer(size);')
					sw.writeln('view = new DataView(array);')
					sw.writeln('view.setUint32(pos,cr.byteLength);')
					sw.writeln('pos += 4;')

					v1 = sw.newVariant('_v')
					sw.writeln('var %s = new Uint8Array(view.buffer);'%(v1,))
					v2 = sw.newVariant('_v')
					sw.writeln('var %s = new Uint8Array(cr);'%(v2,))
					sw.writeln('%s.set(%s,pos);'%(v1,v2) )
					# sw.writeln('pos += %s.buffer.byteLength;'%v2)
				else:
					v = sw.newVariant('_c')
					sw.define_var(v,'%shlp'%m.type.name,'new %shlp(cr)'%m.type.name)
					sw.writeln('size+=%s.getsize();'%v)
					sw.writeln('array = new ArrayBuffer(size);')
					sw.writeln('view = new DataView(array);')
					sw.writeln('pos+=%s.marshall(view,pos);'%v)
			else:
				sw.writeln('size += cr.getsize();')
				sw.writeln('array = new ArrayBuffer(size);')
				sw.writeln('view = new DataView(array);')
				sw.writeln("cr.marshall(view,pos);")

			sw.writeln('mr.paramsize = 1;')
			sw.writeln('mr.paramstream = array;')
			sw.idt_dec().writeln('}catch(e){').idt_inc()
			sw.writeln('console.log(e.toString());')
			sw.writeln('r = false;')
			sw.writeln('return r;')
			sw.scope_end()

			sw.writeln("r =m.conn.sendMessage(mr);") #发送回去
		sw.writeln("return r;")

		sw.scope_end2() # end servant function{}
		sw.wln()
	sw.scope_end() # end class define
#	sw.classfile_leave()
#	sw.pkg_end()



#	createProxy(e,sw,ifidx)

	return


def createCodeInterfaceMapping():
	global interface_defs # {e,f:{}}
	pass




def createCodeFrame(module,e,idx,sw ):
	idt = Indent()

	txt='''
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	'''
	sw.setIncludes('default',(txt,))

	if isinstance(e,Interface):
		#sw.classfile_enter(e.getName())
		createCodeInterface(e,sw,idt,idx)
		#sw.classfile_leave()
		print e.name

#
	if isinstance(e,Sequence):
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
		createCodeStruct(module,e,sw,idt)
		sw.classfile_leave()
		return
#
#	createCodeInterfaceMapping() #创建 链接上接收的tce.Rpc消息 根据其ifx编号分派到对应的接口和函数上去

ostream = sys.stdout

headtitles='''
// -- coding:utf-8 --
//---------------------------------
//  TCE
//  Tiny Communication Engine
//
//  sw2us.com copyright @2012
//  bin.zhang@sw2us.com / qq:24509826
//---------------------------------

	'''+NEWLINE

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
	#file = sys.argv[1]
	global  interface_defs,ifcnt
	file = ''

	ostream = Outputer()
	#ostream.addHandler(sys.stdout)

	argv = sys.argv
	outdir ='.'
	pkgname = ''
	outfile = ''
	filters=''

	while argv:
		p = argv.pop(0)
#		if p =='-o':
#			p = argv.pop(0)
#			f = open(p,'w')
#			ostream.addHandler(f)
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

		# if p =='-filter':
		# 	if argv:
		# 		filters = argv.pop(0)

	if not os.path.exists(outdir):
		os.mkdir(outdir)
	idlfiles = file.strip().split(',')

	# fp = open(file,'r')
	# content = fp.read()
	# fp.close()

#	print outdir
#	os.chdir( outdir )

	for file in idlfiles:
		print file
		idl_file = file
		lexparser.curr_idl_path = os.path.dirname(idl_file)
		parse_idlfile(idl_file)


	# name = os.path.basename(file).split('.')[0]
	#
	# outfile = outdir+'/%s.js'%name
	# sw = StreamWriter(ostream=open(outfile,'w'))


#	ostream.write(headtitles)
	unit = syntax_result()

	# filters = [ x for x in map(string.strip,filters.split(' ')) if x]
	# import tce_util
	# tce_util.filterInterface(unit,filters,ifcnt)

	for module in global_modules:
		name = module.name
		# print 'module:',name,module.ref_modules.keys()
		# print module.children
		f = open(os.path.join(outdir,name+'.js'),'w')
		ostream.clearHandler()
		ostream.addHandler(f)
		ostream.write(headtitles)
		sw = StreamWriter(ostream,Indent())
		# for ref in module.ref_modules.keys():
		# 	sw.writeln('import %s'%ref)

		sw.writeln('define("%s",["tce"],function(tce){'%module.name).wln()

		ifs = []
		for idx,e in enumerate(module.list):
			createCodeFrame(module,e,idx,sw)
			ostream.write(NEWLINE)
			if isinstance(e,Interface):
				ifs.append(e.name)


		sw.writeln('return {').idt_inc()
		#输出模块中的接口列表
		for n in range(len(ifs)):
			ifx = ifs[n]
			sw.writeln('%s : %s,'%(ifx,ifx))
			sw.write('%sProxy : %sProxy'%(ifx,ifx))
			if n <= len(ifs)-2:
				sw.write(',')
			sw.wln()

		sw.idt_dec().writeln('};')

		sw.wln().writeln("});")


	# for idx,e in enumerate(unit.list):
	# 	createCodeFrame(e,idx,sw)
	# 	ostream.write(NEWLINE)


class LanguageJavascript(object):
	language = 'js'
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
			return r


	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			if this.type.name == 'byte':
				return 'new ArrayBuffer(0)'  #
			return '[]'

		@classmethod
		def typeName(cls,this,call_module):
			if this.type.name == 'byte':
				return 'ArrayBuffer'
			return 'Array'


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return '{}'

		@classmethod
		def typeName(cls,this,call_module):
			return ''


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


lexparser.language = 'js'

lexparser.lang_kws = ['for','var','while']
lexparser.codecls = LanguageJavascript

if __name__ =='__main__':
	createCodes()


# usage:
# 	tce2java_xml.py
# 			-i /Users/socketref/Desktop/projects/dvr/ply/code/java/test/sns_mobile_xml.idl
# 				-o /Users/socketref/Desktop/projects/dvr/ply/code/java

