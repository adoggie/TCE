#!/usr/bin/env python

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

import os
import os.path
import string

import lexparser
from lexparser import *
from mylex import syntax_result,parse_idlfile

import tce_util

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
		self.packages =[] #?????
		self.includes ={}
		self.setIncludes('default',[])
		self.defaultinclude = 'deault'
		self.varidx = 0
		self.lastvar =''

	def newVariant(self,name):
		self.varidx +=1
		self.lastvar = "%s_%s"%(name,self.varidx)
		return self.lastvar

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
		txt ="var %s:%s"%(name,type)
		if val:
			txt+=" = "+ val
		txt+=";"
		self.writeln(txt)

	def createPackage(self,name):
		if not  os.path.exists(name):
			os.mkdir(name)

	#?????
	def pkg_enter(self,name):
		self.packages.append(name)
		os.chdir(name)

	def pkg_current(self):
		import string
		return string.join(self.packages,'.')

	def pkg_leave(self):
		pkg = self.packages[-1]
		os.chdir('../')

	def pkg_begin(self):
		pkg = self.packages[-1]
		if not pkg:return
		self.write("package %s"%pkg).brace1().wln().idt_dec()

	def pkg_end(self):
		self.idt_dec().wln().brace2()

	def classfile_enter(self,name,file=''):
		if file:
			self.ostream = open(file+'.as','w')
		else:
			self.ostream = open(name+'.as','w')
		self.pkg_begin()
		#self.idt_inc()
		self.writeIncludes()
		self.idt_inc()

	def classfile_leave(self):
		self.idt_dec()
		self.pkg_end()
		self.ostream.close()



class Builtin_Python:
	def __init__(self):
		pass

	@staticmethod
	def serial(typ,val,idt,sw=None):
		# typ - builtin ; val - variant name
		s=''
		if typ == 'byte':
			sw.writeln("d.writeByte(%s);"%val)
		elif typ == 'bool':
			sw.writeln("if(%s == true){"%val).idt_inc()
			sw.writeln("d.writeByte(1);").idt_dec()
			sw.writeln("}else{").idt_inc()
			sw.writeln("d.writeByte(0);")
#			idt_dec().brace2().wln()
			sw.idt_dec().newline().brace2().wln()


		elif typ == 'short':
			sw.writeln("d.writeShort(%s);"%val)
		elif typ == 'int':
			sw.writeln("d.writeInt(%s);"%val)
		elif typ in ('long','double'):
			sw.writeln("d.writeDouble(%s);"%val)
		elif typ == 'float': #,'double'):
			sw.writeln("d.writeFloat(%s);"%val)
		elif typ =='string':
			# ??4??? ??
			var = sw.newVariant('bytes')
			sw.writeln('var %s:ByteArray = new ByteArray();'%var)
			sw.writeln('%s.writeUTFBytes(%s);'%(var,val))
			sw.writeln("d.writeInt(%s.length);"%var)
			sw.writeln("d.writeBytes(%s);"%var)

		return s

	@staticmethod
	def unserial(typ,val,stream,idt,sw):
		s=''
		if typ == 'byte':
#			s = "%s, = struct.unpack('B',%s[idx:idx+1])"%(val,stream)
#			s+= NEWLINE + idt.str() + "idx+=1"
			sw.writeln("%s = %s.readUnsignedByte();"%(val,stream))
		elif typ == 'bool':
			sw.newline().brace1().wln().idt_inc()
			sw.writeln("var _d:uint = 0;")
			sw.writeln("_d = %s.readUnsignedByte();"%(stream))
			sw.writeln("if(_d == 0){").idt_inc()
			sw.writeln("%s = false;"%val).idt_dec()
			sw.writeln("}else{").idt_inc()
			sw.writeln("%s = true;"%val).idt_dec()
			sw.newline().brace2().wln().idt_dec()
			sw.newline().brace2().wln()
		elif typ == 'short':
			sw.writeln("%s = %s.readShort();"%(val,stream))
		elif typ == 'int':
			sw.writeln("%s = %s.readInt();"%(val,stream))
		elif typ == 'long':
			sw.writeln("%s = %s.readDouble();"%(val,stream))
		elif typ == 'float':
			sw.writeln("%s = %s.readFloat();"%(val,stream))
		elif typ == 'double':
			sw.writeln("%s = %s.readDouble();"%(val,stream))
		elif typ =='string':
			sw.newline().brace1().wln().idt_inc()
			sw.writeln("var _d:uint = 0;")
			sw.writeln("_d = %s.readUnsignedInt();"%(stream))
			sw.writeln("%s = %s.readUTFBytes(_d);"%(val,stream)).idt_dec()
			sw.newline().brace2().wln()

		return s


def createCodeStruct(e,sw,idt):
	#sw = StreamWriter(ostream,idt)
	sw.wln()
	params=[ ]
	for m in e.list:
#		v = m.type.getTypeDefaultValue()
		v = m.type.getMappingTypeName(e.container)
		params.append( (m.name,v) )
	pp =map(lambda x: '%s:%s'%(x[0],x[1]),params)
	ps = string.join(pp,',')
	l ='public class %s{'%e.getName()
	sw.writeln(l)
	sw.writeln("// -- STRUCT -- ")
	sw.idt_inc()

	for m in e.list:
		d = m.type.getTypeDefaultValue(e.container)
		v = m.type.getMappingTypeName(e.container)

		sw.writeln("public var %s:%s = %s;"%(m.name,v,d))
	sw.wln()
	sw.writeln("//????")
	sw.writeln('public function %s(){'%(e.getName(),) )
	sw.idt_inc()
	sw.wln().idt_dec()
	sw.newline().brace2().wln()

	'''
		sw.writeln('def __str__(self):' )
		sw.idt_inc()
		fmt = []
		val =[]
		s =''
		for m in e.list:
			fmt.append('%s:%%s'%m.name)
			val.append('str(self.%s)'%m.name)
		s ="return 'OBJECT<%s :%%s> { %s}'%%(hex(id(self)),%s ) "%( e.getName(),string.join(fmt,','),string.join(val,','))

		sw.writeln(s).wln()

		sw.idt_dec()
	'''

	sw.wln()
	sw.writeln('public function marshall(d:ByteArray):void{')
	sw.idt_inc()

	for m in e.list:
#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			s = Builtin_Python.serial(m.type.type,'this.' + m.name,idt,sw)
			#sw.writeln(s)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			sw.writeln('var container:%shlp = %shlp(this.%s);'%(m.type.name,m.type.name,m.name) )
			sw.writeln('container.marshall(d);' )
			sw.scope_end()
		else:
			sw.scope_begin()
			sw.writeln("this.%s.marshall(d);"% m.name )
			sw.scope_end()
	sw.scope_end()

	sw.wln()

	#unmarshall()
	sw.writeln("//???? unmarshall()")
	sw.writeln("public function unmarshall(d:ByteArray):Boolean{" )

	sw.idt_inc()
	sw.writeln( "try{")
	sw.idt_inc()
	sw.writeln("var r:Boolean = false;")
	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type.type,'this.' + m.name,'d' , idt,sw)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			sw.define_var('container',"%shlp"%m.type.name,"new %shlp(this.%s)"%(m.type.name,m.name) )
			sw.writeln("r = container.unmarshall(d);")
			sw.writeln("if(!r){return false;}")
			sw.scope_end()
		else:
			sw.writeln('r = this.%s.unmarshall(d)'%m.name )
			sw.writeln("if(!r){return false;}")

	sw.idt_dec()
	sw.writeln('}catch(e:Error){' )
	sw.idt_inc()
	sw.writeln('return false;' )
	sw.idt_dec()
	sw.writeln("}")
	sw.writeln('return true;')
	sw.scope_end().writeln(' // --  end function -- ')	# end function
	sw.wln()

	sw.scope_end() # end class


def createCodeSequence(e,sw,idt):
	sw.wln()
#	sw.writeln('import %s;'%e.type.name)
	sw.writeln('public class %shlp{'%e.getName() )
	sw.idt_inc()
	sw.writeln('//# -- SEQUENCE --')
	sw.wln().writeln("public var ds:Array = null;")
	sw.writeln('public function %shlp(ds:Array){'%e.getName() ).idt_inc()
	sw.writeln('this.ds = ds')
	sw.scope_end().wln()

	sw.writeln('public function marshall(d:ByteArray):void{').idt_inc()
	sw.writeln("d.writeInt(this.ds.length);")

	sw.writeln('for(var n:uint=0; n< this.ds.length;n++){').idt_inc()

	if isinstance( e.type,Builtin):
		Builtin_Python.serial(e.type.type,'this.ds[n]',idt,sw)
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		sw.scope_begin()
		sw.define_var('_c','%shlp'%e.type.name,'new %shlp(this.ds[n])'%(e.type.name) )
		sw.writeln('_c.marshall(d);')
		sw.scope_end()
	else:
		sw.writeln("this.ds[n].marshall(d);")

	sw.scope_end()
	sw.scope_end()
	sw.wln()
	#def unmarshall()

	sw.writeln('public function unmarshall(d:ByteArray):Boolean{').idt_inc()
	sw.writeln("var r:Boolean = false;")
	sw.writeln("try{").idt_inc()
	sw.define_var("_size","uint","0")
	sw.writeln("_size = d.readUnsignedInt();")
	sw.writeln("for(var _p:uint=0;_p < _size;_p++){").idt_inc()


	if isinstance(e.type,Builtin):
		sw.scope_begin()
		sw.define_var("_o",e.type.getMappingTypeName(e.container),e.type.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.type.type,'_o','d',sw.idt,sw)
		sw.writeln("this.ds.push(_o);")
		sw.scope_end()
	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):
		sw.scope_begin()
		if isinstance( e.type,Sequence):
			sw.define_var("_o","Array","new Array()")
		else:
			sw.define_var("_o","HashMap","new HashMap()")
		sw.define_var("container","%shlp"%e.type.name,"new %shlp(_o)"%e.type.name)
		sw.writeln("r = container.unmarshall(d);")
		sw.writeln("if(!r) return false;")
		sw.writeln("this.ds.push(_o);")
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var("_o",e.type.name,"new %s()"%e.type.name)
		sw.writeln("r= _o.unmarshall(d);")
		sw.writeln("if(!r) return false;")
		sw.writeln("this.ds.push(_o);")
		sw.scope_end()

	sw.scope_end() # end for{}

	sw.idt_dec()
	sw.writeln("}catch(e:Error){").idt_inc()
	sw.writeln("return false;")
	sw.scope_end()

	sw.writeln("return true;")
	sw.scope_end()

	sw.wln()
	sw.scope_end()
	sw.wln()



def createCodeDictionary(e,sw,idt):

	sw.wln()
	sw.writeln('public class %shlp {'%e.getName() ).idt_inc()
	sw.writeln('//# -- THIS IS DICTIONARY! --')
	sw.writeln('public var ds :HashMap = null;').wln()
	sw.writeln('public function %shlp(ds:HashMap){'%e.getName() ).idt_inc()	#?hash??{}????
	sw.writeln('this.ds = ds;')
	sw.scope_end()
	sw.wln()

	sw.writeln('public function marshall(d:ByteArray):void{').idt_inc()
#	sw.writeln("d += struct.pack('!I',len(this.ds.keys()))" )

	sw.writeln("var _size:uint = 0;")
	sw.writeln("_size = this.ds.size();")
	sw.writeln('d.writeUnsignedInt( this.ds.size() );')
	sw.writeln('var _items:Array;')
	sw.writeln('var _pair: HashMapEntry;')

	sw.writeln('_items = this.ds.getEntries();')
	sw.writeln('for(var _n:int=0; _n < _items.length ; _n++){').idt_inc()
	sw.writeln('_pair = _items[_n] as HashMapEntry;')

	if isinstance( e.first,Builtin):
		sw.scope_begin()
		sw.define_var('k',e.first.getMappingTypeName(e.container),'_pair.key as %s'%e.first.getMappingTypeName(e.container))
		Builtin_Python.serial(e.first.type,'k',idt,sw)
		sw.scope_end()
	elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
		sw.scope_begin()
		if isinstance(e.first,Sequence):
			sw.define_var('container','%shlp'%e.first.name,'new %shlp(_pair.key as Array)'%(e.first.name) )
		else:
			sw.define_var('container','%shlp'%e.first.name,'new %shlp(_pair.key as HashMap)'%(e.first.name) )
		sw.writeln('container.marshall(d);')
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var('k',e.first.getMappingTypeName(e.container),'_pair.key as %s'%e.first.getMappingTypeName(e.container) )
		sw.writeln("k.marshall(d);")
		sw.scope_end()

	if isinstance( e.second,Builtin):
		sw.scope_begin()
		sw.define_var('v',e.second.getMappingTypeName(e.container),'_pair.value as %s'%e.second.getMappingTypeName(e.container))
		Builtin_Python.serial(e.second.type,'v',idt,sw)
		sw.scope_end()
	elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
		sw.scope_begin()
		if isinstance(e.second,Sequence):
			sw.define_var('container','%shlp'%e.second.name,'new %shlp(_pair.value as Array)'%(e.second.name) )
		else:
			sw.define_var('container','%shlp'%e.second.name,'new %shlp(_pair.value as HashMap)'%(e.second.name) )
		sw.writeln('container.marshall(d);')
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var('v',e.second.getMappingTypeName(e.container),'_pair.value as %s'%e.second.getMappingTypeName(e.container))
		sw.writeln("v.marshall(d);")
		sw.scope_end()
	sw.scope_end() # end for
	sw.scope_end() # end function
	sw.wln()

	#def unmarshall()
	sw.writeln("// unmarshall()")
	sw.writeln('public function unmarshall(d:ByteArray):Boolean{').idt_inc()
	sw.writeln("var r:Boolean = false;")
	sw.writeln("try{").idt_inc()
	sw.define_var("_size","uint","0")
	sw.writeln("_size = d.readUnsignedInt();")




	sw.writeln("for(var _p:uint=0;_p < _size;_p++){").idt_inc()

	if isinstance(e.first,Builtin):
		sw.define_var("_k",e.first.getMappingTypeName(e.container),e.first.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.first.type,'_k','d',sw.idt,sw)
	elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
		sw.define_var("_k",e.first.getMappingTypeName(e.container),e.first.getTypeDefaultValue(e.container) )
		sw.define_var('_c1','%shlp'%e.first.name,'new %shlp(_k)'%e.first.name)
		sw.writeln('r = _c1.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_k",e.first.getMappingTypeName(e.container),e.first.getTypeDefaultValue(e.container) )
		sw.writeln('r = _k.unmarshall(d);')
		sw.writeln('if(!r) return false;')

	if isinstance(e.second,Builtin):
		sw.define_var("_v",e.second.getMappingTypeName(e.container),e.second.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.second.type,'_v','d',sw.idt,sw)
	elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
		sw.define_var("_v",e.second.getMappingTypeName(e.container),e.second.getTypeDefaultValue(e.container) )
		sw.define_var('_c2','%shlp'%e.second.name,'new %shlp(_k)'%e.second.name)
		sw.writeln('r = _c2.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_v",e.second.getMappingTypeName(e.container),e.second.getTypeDefaultValue(e.container) )
		sw.writeln('r = _v.unmarshall(d);')
		sw.writeln('if(!r) return false;')


	sw.writeln("this.ds[_k] = _v;")
	sw.scope_end() # end for
	sw.idt_dec()
	sw.wln()
	sw.writeln('}catch(e:Error){').idt_inc()
	sw.writeln('return false;')
	sw.scope_end()


	sw.writeln('return true;')
	sw.scope_end()	# end function

	sw.scope_end() # end class
	sw.writeln('//-- end Dictonary Class definations --')
	sw.wln()


'''
1.?? ??? ????dispatch ???
2.?? ????? prx
'''


'''
dummy code:
-------------

???????
class a_delegate:
	def __init__(self,inst_a,conn):
		self.inst = inst_a
		self.conn = conn

	def call_1(self,stream):
		p1 = Class1()
		p1.unmarshall(stream)
		p2 = Class2()
		p2.unmarshall(stream)

		cr = self.inst.call_1(p1,p2)
		d = cr.marshall()
		conn.sendMessage(d)

??????????????
class a_proxy:
	def __init__(self,conn):
		self.conn = conn

	def call_1(self,p1,p2):
		d = p1.marshall()
		d += p2.marshall()
		self.conn.sendMessage(d)

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
fileifx = open('ifxdef.txt','w') #?????

def createCodeInterface(e,sw,idt,idx):
	global  interface_defs,ifcnt
	ifidx = e.ifidx
	ifcnt+=1


	import tce_util
	# ifname = "%s.%s"%(e.container.name,e.name)
	# r = tce_util.getInterfaceIndexWithName(ifname)
	# if r != -1:
	# 	ifidx = r
	# #--- end
	# e.ifidx = ifidx

	ifidx = e.index
	interface_defs[ifidx] = {'e':e,'f':{}}

	createInterfaceProxy(e,sw,ifidx)

	# expose = tce_util.isExposeDelegateOfInterfaceWithName(ifname)
	# if not expose:
	# 	return
	if not tce_util.generateSkeleton(e,lexparser.language):
		return

	sw.classfile_enter(e.getName())
	sw.writeln('import tcelib.RpcServant;')
	sw.writeln('import tcelib.RpcContext;')
	sw.writeln('import %s.%s_delegate;'%(sw.pkg_current(),e.getName()) )
	sw.wln()

	sw.writeln('public class %s extends RpcServant{'%e.getName() )
	sw.idt_inc()
	sw.writeln("//# -- INTERFACE -- ")
#	sw.writeln('var delegatecls:Class = %s_delegate'%e.getName())
	#?????delegate ???
	sw.writeln("public function %s(){"%e.getName() ).idt_inc()
	sw.writeln('this.delegate = new %s_delegate(this);'%e.getName())
	sw.scope_end().wln()

	for m in e.list: # function list
		sw.wln()
		params=[]
		for p in m.params:
			params.append( (p.id,p.type.getMappingTypeName(e.container)) )
		list =[]
		for v,t in params:
			list.append('%s:%s'%(v,t))
		s = string.join( list,',')
		if s: s += ','
		sw.writeln('public function %s(%sctx:RpcContext = null):%s{'%(m.name,s,m.type.getMappingTypeName(e.container) ) ).idt_inc()
		#------------????????----------------------

		if isinstance( m.type ,Builtin ):
			if m.type.type =='void':
#				sw.idt_dec().wln()
				sw.scope_end()
				continue
			else:
				sw.writeln("return %s;"%m.type.getTypeDefaultValue(e.container))
		elif isinstance(m.type,Sequence):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(e.container) )
		elif isinstance(m.type,Dictionary):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(e.container) )
		else:
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(e.container) )
		sw.scope_end()

	sw.scope_end() # end class


	sw.classfile_leave()

#	sw.pkg_end()

	#----------------------------------
	sw.classfile_enter("%s_delegate"%e.getName())

	sw.writeln('import tcelib.*;')
	sw.writeln("import tcelib.utils.HashMap;")
	sw.writeln("import flash.utils.ByteArray;")
	sw.writeln("import flash.utils.Endian;")

	sw.writeln("import tcelib.RpcServantDelegate;")

#	sw.writeln("import %s;"%e.getName())
	sw.wln()
	#????????
	sw.writeln("public class %s_delegate extends RpcServantDelegate {"%e.getName()).idt_inc()

	sw.wln()
#	sw.writeln('var index:uint = %s;'%ifidx)
#	sw.writeln('var id:String;')
#	sw.writeln('var adapter:RpcCommAdapter = null;')
	sw.writeln('public var conn:RpcConnection = null;')
#	sw.writeln('var inst:%s = null;'%(e.getName()))
	sw.wln()

	sw.writeln("public function %s_delegate(inst:%s,adapter:RpcCommAdapter=null,conn:RpcConnection=null){"%(e.getName(),e.getName() )).idt_inc()
#	sw.writeln('this.id = ""; ')  #?????
	sw.writeln("this.adapter = adapter;")
	sw.writeln('this.index = %s;'%ifidx)
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.writeln("this.optlist.put(%s,this.%s);"%(opidx,m.name)) #???? twoway ? oneway ????

	sw.writeln("this.inst = inst;")
	sw.scope_end().wln()

	#???? ????
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.writeln('public function %s(ctx:RpcContext = null):Boolean{'%(m.name) ).idt_inc()

		params=[ ]
		sw.define_var('d','ByteArray')
		sw.writeln("d = ctx.msg.paramstream; ")
		sw.writeln('var r:Boolean = false;')
		#sw.writeln("idx = 0")
		#?????????? _p_??
		for p in m.params:
			if isinstance(p.type,Builtin):
				sw.define_var(p.id,p.type.getMappingTypeName(e.container))
				Builtin_Python.unserial(p.type.type,p.id,'d',idt,sw)
			elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
				sw.define_var(p.id,p.type.getMappingTypeName(e.container),'new %s()'%p.type.getMappingTypeName(e.container))
				sw.scope_begin()
				sw.define_var('_c','%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
				sw.writeln('r = _c.unmarshall(d);')
				sw.writeln('if(!r) return false;')
				sw.scope_end()

			else:
				sw.define_var(p.id,p.type.getMappingTypeName(e.container),'new %s()'%p.type.getMappingTypeName(e.container))

				sw.writeln('r = %s.unmarshall(d);'%p.id)
				sw.writeln('if(!r) return false;')


			params.append(p.id)
		#params = map( lambda x: '_p_'+x,params)
		ps = string.join(params,',')

		if ps: ps = ps + ','
		sw.define_var('servant',e.getName(),'this.inst as %s'%e.getName())
		if isinstance(m.type,Builtin) and m.type.type =='void':
			sw.writeln("servant.%s(%sctx)"%(m.name,ps) )
		else:
			sw.define_var('cr',m.type.getMappingTypeName(e.container))
			sw.writeln("cr = servant.%s(%sctx)"%(m.name,ps) )

#			sw.writeln("if cr == None:").idt_inc()
#			if isinstance(m.type,Sequence):
#				sw.writeln("cr = []")
#				sw.idt_dec()
#			elif isinstance(m.type,Dictionary):
#				sw.writeln("cr = {}")
#				sw.idt_dec()
#			else:
#				sw.writeln("pass").idt_dec()


		sw.writeln("if( ctx.msg.calltype & tcelib.RpcMessage.CALL_ONE_WAY){").idt_inc()
		sw.writeln("return false;")
		sw.scope_end()

		sw.wln()

#		sw.define_var('d','ByteArray','new ByteArray();')
		sw.writeln('d = new ByteArray();')
		sw.writeln('d.endian = Endian.BIG_ENDIAN;')
		sw.define_var('m','RpcMessageReturn','new RpcMessageReturn()')
		sw.writeln("m.sequence = ctx.msg.sequence;") #???????????????


		if isinstance( m.type ,Builtin ):
			Builtin_Python.serial(m.type.type,'cr',idt,sw)

		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			v = sw.newVariant('_c')
			sw.define_var(v,'%shlp'%m.type.name,'new %shlp(cr)'%m.type.name)
			sw.writeln('%s.marshall(d);'%v)
			sw.scope_end()
		else:
			sw.writeln("cr.marshall(d);")


		sw.writeln("if(d.length) m.addParam(d);")
		sw.writeln("ctx.conn.sendMessage(m);")
		sw.writeln("return true;")

		sw.scope_end()
		sw.wln()
	sw.scope_end()
	sw.classfile_leave()
#	sw.pkg_end()

def createInterfaceProxy(e,sw,ifidx):
	#------------Create Proxy -------------
	# ????
	sw.classfile_enter('%sPrx'%e.getName())
#	sw.wln()
	sw.writeln('import tcelib.RpcProxyBase;')
	sw.writeln('import tcelib.RpcMessageCall;')
	sw.writeln('import tcelib.RpcMessage;')
	sw.writeln('import tcelib.RpcExtraData;')
#	sw.writeln('import tcelib.*;')
#	sw.writeln("import tcelib.utils.HashMap;")
#	sw.writeln("import flash.utils.ByteArray;")
#	sw.writeln("import flash.utils.Endian;")
#	sw.writeln("import tcelib.RpcProxyBase;")


#	sw.writeln("import %s.%s;"%(sw.pkg_current(), e.getName() ) )
	sw.wln()




	sw.writeln('public class %sPrx extends RpcProxyBase{'%e.getName() ).idt_inc()
	sw.writeln("//# -- INTERFACE PROXY -- ")
#	sw.writeln('var conn:RpcConnection ;')
	sw.writeln('public var delta:Object = null;')
	sw.wln()
	sw.writeln("public function  %sPrx(conn:RpcConnection){"%(e.getName())).idt_inc()
	sw.writeln("this.conn = conn;")
	sw.scope_end()


	#--create()
	sw.writeln('public static function create(host:String,port:int):%sPrx{'%e.getName()).idt_inc()
	sw.writeln('var conn:RpcConnection = new RpcConnection();')
	sw.writeln('conn.open(host,port);')
	sw.writeln('var prx:%sPrx = new %sPrx(conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()

	#--createWithProxy()
	sw.writeln('public static function createWithProxy(proxy:RpcProxyBase):%sPrx{'%e.getName()).idt_inc()
	sw.writeln('var prx:%sPrx = new %sPrx(proxy.conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()
	#-- end create()
	sw.wln()


	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.wln()
		params=[]

		interface_defs[ifidx]['f'][opidx] = m	#?????????
		list =[]
		for p in m.params:
#			params.append( p.id,p.type.getMappingTypeName())
			list.append('%s:%s'%(p.id,p.type.getMappingTypeName(e.container)))
		s = string.join( list,',')
		# ??????
		if s: s = s + ','
		sw.writeln('public function %s(%sasync:Function = null,extra:RpcExtraData=null):int{'%(m.name,s,) ).idt_inc()
		sw.writeln("//# function index: %s"%opidx).wln()
		sw.define_var('r','Boolean','false')
		sw.writeln("try{").idt_inc()
		sw.define_var('ecode','int','tcelib.RpcConsts.RPCERROR_SUCC')
		sw.writeln("ecode = tcelib.RpcConsts.RPCERROR_SUCC;")
		sw.define_var('m','tcelib.RpcMessageCall','new tcelib.RpcMessageCall()')

		sw.writeln("m.ifidx = %s;"%ifidx)
		sw.writeln("m.opidx = %s;"%opidx)
		sw.writeln("if( extra!=null){").idt_inc()
		sw.writeln("m.extra = extra;").scope_end().idt_dec()

		sw.define_var('d','ByteArray')
#		sw.define_var('_h','HashMap','new HashMap()')
		for p in m.params:
			sw.writeln('d = new ByteArray();')
			if isinstance(p.type,Builtin):
				Builtin_Python.serial(p.type.type,p.id,sw.idt,sw)
			elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
				v = sw.newVariant('_c')
#				sw.writeln('_ar = new ByteArray();')
				sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
				sw.writeln('%s.marshall(d);'%v)
			elif isinstance(p.type,Dictionary):
				v = sw.newVariant('_c')
#				sw.writeln('_h = new HashMap();')
				sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
				sw.writeln('%s.marshall(d);'%v)
			else:
				sw.writeln("%s.marshall(d);"%p.id)
			sw.writeln("m.addParam(d);")
		sw.writeln("m.prx = this as Object;")
		sw.writeln("m.async = async;")
		sw.writeln("m.asyncparser = this.%s_asyncparser as Function;"%(m.name ) )
		sw.writeln("r = this.conn.sendMessage(m);")
		sw.writeln("if(!r){").idt_inc()
		sw.writeln("ecode = tcelib.RpcConsts.RPCERROR_SENDFAILED;")
		sw.writeln("return ecode;")
		sw.scope_end()

#		sw.writeln("if(async == null){").idt_inc()
#		sw.writeln("return tcelib.RpcConsts.RPCERROR_SUCC;")
#		sw.scope_end()

		sw.idt_dec()
		sw.writeln("}catch(e:Error){").idt_inc()
		sw.writeln("return tcelib.RpcConsts.RPCERROR_DATADIRTY;")
		sw.scope_end()
		sw.writeln("return tcelib.RpcConsts.RPCERROR_SUCC;")
		sw.scope_end()
		#end --

		sw.wln()



		# -- ?? ???? ????? ????? ?????
		sw.writeln('private  function %s_asyncparser(m:RpcMessage,m2:RpcMessage):void{'%(m.name,) ).idt_inc()
		sw.writeln("//# function index: %s , m2 - callreturn msg."%opidx).wln() #stream,user,prx)

		if m.type.name !='void':
			sw.define_var('stream','ByteArray')
			sw.writeln("stream = m2.paramstream;")
			sw.define_var('user','Function')
			sw.writeln("user = m.async;")
	#		sw.define_var('prx','%sPrx'%e.name)
	#		sw.writeln("prx = m.prx as %sPrx;"%e.name)
			#????????????? ??????????????????
			sw.writeln("if(m2.errcode != tcelib.RpcConsts.RPCERROR_SUCC) return; ") #skipped error

			#void ??????
			sw.writeln("if(stream.length == 0){ ").idt_inc() #???????return is 'void'
			sw.writeln("user(this);")
			sw.writeln("return;")
			sw.scope_end()

			sw.writeln("try{").idt_inc()
	#
			sw.define_var('d','ByteArray')
			sw.writeln("d = stream;")
#			sw.define_var('r','Boolean','true')

			if isinstance(m.type,Builtin):
				sw.define_var('_p',m.type.getMappingTypeName(e.container),m.type.getTypeDefaultValue(e.container))
				Builtin_Python.unserial(m.type.type,'_p','d',sw.idt,sw)
			elif isinstance(m.type,Sequence):
				sw.define_var('_p','Array','new Array()')
				sw.define_var('_c','%shlp'%m.type.name,'new %shlp(_p)'%m.type.name)
				sw.writeln(' _c.unmarshall(d);')
			elif isinstance(m.type,Dictionary):
				sw.define_var('_p','HashMap','new HashMap()')
				sw.define_var('_c','%shlp'%m.type.name,'new %shlp(_p)'%m.type.name)
				sw.writeln('_c.marshall(d);')
			else:
				sw.define_var('_p',m.type.name,'new %s()'%m.type.name)
	#
				sw.writeln('_p.unmarshall(d);')
#			sw.writeln("if(!r){ user(_p,this); }")
			sw.writeln('user(_p,this);')

			sw.idt_dec()
			sw.writeln("}catch(e:Error){").idt_inc()
			sw.writeln("trace(e.toString());")
			sw.writeln('return ;')
			sw.scope_end()

		sw.scope_end() # end for function

		sw.wln()
		#------------------------
		#-- ??oneway????? (????????)
		'''
		params =[]
		list=[]
		for p in m.params:
			params.append( p.id )
			list.append('%s:%s'%(p.id,p.type.getMappingTypeName()))
		s = string.join( list,',')
		if s: s = s

		sw.writeln('public function %s_onway(%s):Boolean{'%(m.name,s) ).idt_inc()
		sw.writeln("//# function index: %s"%idx).wln()
		sw.define_var('r','Boolean','true')
		sw.writeln("try{").idt_inc()
		sw.define_var('m','tcelib.RpcMessageCall')
		sw.writeln("m = tcelib.RpcMessageCall();")
		sw.writeln("m.ifidx = %s;"%ifidx)
		sw.writeln("m.opidx = %s;"%opidx)
		sw.writeln("m.calltype = tcelib.RpcMessageCall.ONEWAY_CALL;")

		for p in m.params:
			sw.writeln("var d :Array= new Array(); ")
			if isinstance(p.type,Builtin):
				Builtin_Python.serial(p.type.type,p.id,idt,sw)
			elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
				sw.scope_begin()
				sw.define_var('_c','%shlp'%p.type.name,'%shlp(%s)'%(p.type.name,p.id))
				sw.writeln('_c.marshall(d);')
				sw.scope_end()
			else:
				sw.writeln('%s.marshall(d);'%p.id)

			sw.writeln("m.addParam(d)")

		sw.writeln("r = this.conn.sendMessage(m);")
		sw.writeln('if(!r) return false;')
		sw.idt_dec()
		sw.writeln("}catch(e:Error){").idt_inc()
		sw.writeln("return false;")
		sw.scope_end()
		sw.writeln('return true;')
		sw.scope_end() # end function
		sw.wln()
		'''
	#-- end onway --------------
	sw.scope_end() # end class  '}'
	sw.classfile_leave()

	# --  begin ???? ---

	# --  end ???? ---



	return
#
'''
???

def

'''


def createCodeInterfaceMapping():
	global interface_defs # {e,f:{}}
	pass




def createCodeFrame(e,idx,sw ):
	idt = Indent()

	txt='''
	import tcelib.RpcConsts;
	import tcelib.RpcConnection;
	import tcelib.utils.HashMap;
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	import tcelib.utils.HashMapEntry;
	'''
	sw.setIncludes('default',(txt,))

	if isinstance(e,Interface):
		#sw.classfile_enter(e.getName())
		createCodeInterface(e,sw,idt,idx)
		#sw.classfile_leave()


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

	if isinstance(e,Struct):
		sw.classfile_enter(e.getName())
		createCodeStruct(e,sw,idt)
		sw.classfile_leave()
		return
#
#	createCodeInterfaceMapping() #?? ??????Rpc?? ???ifx???????????????

ostream = sys.stdout

headtitles='''
# -- coding:utf-8 --

#---------------------------------
#  TCE
#  Tiny Communication Engine
#
#  sw2us.com copyright @2012
#  bin.zhang@sw2us.com / qq:24509826
#---------------------------------

import os,os.path,sys,struct,time,traceback,time
import tcelib

	'''+NEWLINE

class Outputer:
	def __init__(self):
		self.files = []

	def addHandler(self,h):
		self.files.append(h)
		return self

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
	ostream.addHandler(sys.stdout)

	argv = sys.argv
	outdir ='./output'
	pkgname = ''
	filters=''
	while argv:
		p = argv.pop(0)
#		if p =='-ox':
#			p = argv.pop(0)
#			f = open(p,'w')
#			ostream.addHandler(f)
		if p == '-o':
			if argv:
				p = argv.pop(0)
				outdir = p
		if p =='-if': # ??????????module??????????????
			ifcnt = int(argv.pop(0))

		if p =='-i':
			if argv:
				p = argv.pop(0)
				file = p
		if p == '-p':
			pkgname = argv.pop(0)
		if p =='-filter':
			filters = argv.pop(0)

	fp = open(file,'r')
	content = fp.read()
	fp.close()

	if not os.path.exists(outdir):
		os.mkdir(outdir)



	idlfiles = file.strip().split(',')

	for file in idlfiles:
		lexparser.curr_idl_path = os.path.dirname(file)
		parse_idlfile(file)

	unit = syntax_result()
	os.chdir( outdir )

	sw = StreamWriter()

	if not pkgname:
		pkgname = os.path.basename(file).split('.')[0]

	sw.createPackage(pkgname)
	sw.pkg_enter(pkgname)
#	ostream.write(headtitles)
	# unit = syntax_result(content)
	# filters = [ x for x in map(string.strip,filters.split(' ')) if x]
	sys.path.append(os.path.dirname(__file__))
	import tce_util
	tce_util.filterInterface(unit, filters, ifcnt)

	print global_modules_defs

	for module in global_modules:

		for idx,e in enumerate(module.list):
			createCodeFrame(e,idx,sw)
#		ostream.write(NEWLINE)

	sw.pkg_leave()



class LanguageActionScript(object):
	language = 'as'
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

			return r


	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			# if this.type.name == 'byte':
			# 	return 'new ArrayBuffer(0)'  #
			return 'new Array()'

		@classmethod
		def typeName(cls,this,call_module):
			# if this.type.name == 'byte':
			# 	return 'ArrayBuffer'
			return 'Array'


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'new HashMap()'

		@classmethod
		def typeName(cls,this,call_module):
			return 'HashMap'


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

lexparser.language = 'as'

lexparser.lang_kws = ['for','var','while']
lexparser.codecls = LanguageActionScript

if __name__ =='__main__':
	createCodes()

"""
usage:
tce2as.py -i service.idl,.. -o output_dir
"""
"""
tce2as.py :
	sw.newVariant() is not implemented.
	Tobe Next..
"""
