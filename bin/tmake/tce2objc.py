#--coding:utf-8--

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
#  tce for objc
# scott 2014-1-19

import os
import os.path
import string

import lexparser
from lexparser import *
from mylex import syntax_result,parse_idlfile

H_FILE = 0
MM_FILE = 1

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
		self.ostream1 =None
		self.ostream2 =None

		self.ostreams = []
		self.ostream = None

		self.idt = Indent()
		self.packages =[] #当前包名称
		self.includes ={}
		self.setIncludes('default',[])
		self.defaultinclude = 'deault'
		self.varidx = 0
		self.lastvar =''


	def setstream(self,which = 0):
		'''
		'''
		self.ostream = self.ostreams[which]
		return self

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
		ostream1 = open(name+'.h','w')
		ostream2 = open(name+'.mm','w')
		self.ostreams =[ostream1,ostream2]
		self.setstream(H_FILE)
		self.writeln('#import "RpcByteArray.h"')
		self.writeln('#import "RpcProxyBase.h"')
		self.writeln('#import "RpcAsyncCallBackBase.h"')
		self.writeln('#import "RpcCommAdapter.h"')
		self.writeln('#import "RpcCommunicator.h"')

		self.writeln('#import "RpcConnection.h"')
		self.writeln('#import "RpcConsts.h"')
		self.writeln('#import "RpcContext.h"')
		self.writeln('#import "RpcException.h"')
		self.writeln('#import "RpcLogger.h"')
		self.writeln('#import "RpcMessage.h"')
		self.writeln('#import "RpcServant.h"')
		self.writeln('#import "RpcServantDelegate.h"')
		self.setstream(MM_FILE)
		self.writeln('#import "%s.h"'%name)

		# if not  os.path.exists(name):
		# 	print 'mkdir:',name
		# 	os.mkdir(name)

	#进入包空间
	def pkg_enter(self,name):
		return
		# self.packages.append(name)
		# os.chdir(name)


	def pkg_current(self):
		import string
		return string.join(self.packages,'.')

	def pkg_leave(self):
		pass
		# pkg = self.packages[-1]
		# os.chdir('../')

	def pkg_begin(self):
		pkg = self.packages[-1]
		if not pkg:return
#		self.write("package %s"%pkg).brace1().wln().idt_dec()
#		print pkg
		self.idt.reset()
		self.write("package %s;"%pkg)

	def pkg_end(self):
		pass
#		self.idt_dec().wln().brace2()

	def classfile_enter(self,name,file=''):
		pass
		# if file:
		# 	self.ostream = open(file+'.java','w')
		# else:
		# 	self.ostream = open(name+'.java','w')
		# self.pkg_begin()
		# self.writeIncludes()

	def classfile_leave(self):
		pass
		# self.idt_dec()
		# self.pkg_end()
		# self.ostream.close()



class Builtin_Python:
	def __init__(self):
		pass

	'java default: BIG_ENDIAN '
	@staticmethod
	def serial(typ,val,sw,stream):
		# typ - builtin object ; val - variant name; var = d
		s=''
		if typ.type =='byte':
			sw.writeln('[%s writeByte:(uint8_t)%s];'%(stream,val))
		if typ.type =='short':
			sw.writeln('[%s writeInt16:(int16_t)%s];'%(stream,val))
		if typ.type =='int':
			sw.writeln('[%s writeInt32:(int32_t)%s];'%(stream,val))
		if typ.type =='long':
			sw.writeln('[%s writeInt64:(int64_t)%s];'%(stream,val))
		if typ.type =='float':
			sw.writeln('[%s writeFloat:(float)%s];'%(stream,val))
		if typ.type =='double':
			sw.writeln('[%s writeDouble:(double)%s];'%(stream,val))
		if typ.type =='string':
			sw.writeln('[%s writeString:%s];'%(stream,val))
		if typ.type == 'bool':
			sw.writeln('[%s writeByte: %s==true?1:0 ];'%(stream,val))
		return s

	@staticmethod
	def serial2(typ,val,sw,stream):
		# typ - builtin object ; val - variant name; var = d
		# val -(NSNumber*) 处理 sequence<nsnumber*>类型
		s=''
		if typ.type =='byte':
			sw.writeln('[%s writeByte:[%s unsignedCharValue] ];'%(stream,val))
		if typ.type =='short':
			sw.writeln('[%s writeInt16:[%s shortValue] ];'%(stream,val))
		if typ.type =='int':
			sw.writeln('[%s writeInt32:[%s intValue] ];'%(stream,val))
		if typ.type =='long':
			sw.writeln('[%s writeInt64:[%s longLongValue]];'%(stream,val))
		if typ.type =='float':
			sw.writeln('[%s writeFloat:[%s floatValue]];'%(stream,val))
		if typ.type =='double':
			sw.writeln('[%s writeDouble:[%s doubleValue]];'%(stream,val))
		if typ.type =='string':
			sw.writeln('[%s writeString:%s];'%(stream,val))
		if typ.type == 'bool':
			sw.writeln('[%s writeByte: [%s unsignedCharValue] ];'%(stream,val))
		return s


	@staticmethod
	def unserial(typ,val,sw,stream):
		s=''
		if typ.type =='byte':
			sw.writeln('%s = [%s readByte];'%(val,stream))
		if typ.type =='short':
			sw.writeln('%s = [%s readInt16];'%(val,stream))
		if typ.type =='int':
			sw.writeln('%s = [%s readInt32];'%(val,stream))
		if typ.type =='long':
			sw.writeln('%s = [%s readInt64];'%(val,stream))
		if typ.type =='float':
			sw.writeln('%s = [%s readFloat];'%(val,stream))
		if typ.type =='double':
			sw.writeln('%s = [%s readDouble];'%(val,stream))
		if typ.type =='string':
			sw.writeln('%s = [%s readString];'%(val,stream))
		if typ.type == 'bool':
			sw.writeln('%s = [%s readByte]==0?false:true;'%(val,stream))
		return s

	@staticmethod
	def unserial2(typ,val,sw,stream):
		'''
			还原到 sequence<nsnumber*>类型
		'''

		s=''
		if typ.type =='byte':
			sw.writeln('%s =[NSNumber numberWithUnsignedChar: [%s readByte] ];'%(val,stream))
		if typ.type =='short':
			sw.writeln('%s =[NSNumber numberWithShort:[%s readInt16] ];'%(val,stream))
		if typ.type =='int':
			sw.writeln('%s =[NSNumber numberWithInt:[%s readInt32] ];'%(val,stream))
		if typ.type =='long':
			sw.writeln('%s =[NSNumber numberWithLongLong:[%s readInt64] ];'%(val,stream))
		if typ.type =='float':
			sw.writeln('%s =[NSNumber numberWithFloat:[%s readFloat] ];'%(val,stream))
		if typ.type =='double':
			sw.writeln('%s =[NSNumber numberWithDouble [%s readDouble] ];'%(val,stream))
		if typ.type =='string':
			sw.writeln('%s = [%s readString];'%(val,stream))
		if typ.type == 'bool':
			sw.writeln('%s = [NSNumber numberWithUnsignedChar:[%s readByte] ];'%(val,stream))
		return s

def createCodeStruct(e,sw,idt):
	#sw = StreamWriter(ostream,idt)
	sw.setstream(H_FILE)
	module = e.container
	sw.wln()
	sw.writeln('@interface %s:NSObject'%e.getName()).idt_inc()
	for m in e.list:
		v = m.type.getMappingTypeName(module)
		sw.writeln("@property %s %s;"%(v,m.name))
	sw.wln()
	sw.writeln('-(void)marshall:(RpcByteArray*)bar;')
	sw.writeln('-(void)unmarshall:(RpcByteArray*)bar;')
	sw.wln().idt_dec()
	sw.writeln('@end')

	# .mm file
	# init,marshall,unmarshall
	sw.setstream(MM_FILE)
	sw.wln()
	sw.writeln('@implementation %s'%e.getName()).wln()
	sw.writeln('-(id)init{').idt_inc()
	sw.writeln('self =[super init];')

	for m in e.list:
		# v = m.type.getMappingTypeName(module)
		v = m.type.getTypeDefaultValue(module)
		sw.writeln('self.%s = %s;'%(m.name,v))
	sw.writeln('return self;')
	sw.scope_end()


	#定义序列化函数
	sw.wln()
	sw.resetVariant()

	sw.writeln('-(void)marshall:(RpcByteArray*)bar{').idt_inc()
	for m in e.list:
#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			Builtin_Python.serial(m.type, 'self.'+m.name,sw,'bar')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			impled = False
			if isinstance(m.type,Sequence) :
				if m.type.type.name=='byte':
					# sw.writeln('[bar writeUInt32:(uint32_t)[self.%s length] ];'%(m.name)) # byte -> NSData*
					sw.writeln('[bar writeData:self.%s];'%(m.name))
					impled = True
			if not impled:
				v = sw.newVariant('v')
				sw.writeln('%shlp* %s = [%shlp new];'%(m.type.name,v,m.type.name))
				sw.writeln('%s.data=self.%s;'%(v,m.name))
				sw.writeln('[%s marshall:bar];'%(v))
		else:
			sw.writeln('[self.%s marshall:bar];'%m.name)

	sw.scope_end() # end function
	sw.wln()

	#unmarshall()
	sw.resetVariant()
	sw.writeln("-(void) unmarshall:(RpcByteArray *) bar{" ).idt_inc()

	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type,'self.'+m.name,sw,'bar')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			impled = False
			if isinstance(m.type,Sequence):
				if m.type.type.name == 'byte':
					size = sw.newVariant('v')
					# sw.writeln('uint32_t %s = [bar readUInt32];'%(size))
					# sw.writeln('self.%s = [NSMutableData new];'%(m.name))
					sw.writeln('self.%s = [bar readData];'%(m.name))
					# sw.writeln('[self.%s setData: [bar readData:%s] ];'%(m.name,size))
					impled = True
			if not impled:
				v = sw.newVariant('v')
				sw.writeln('%shlp* %s = [%shlp new];'%(m.type.name,v,m.type.name))
				sw.writeln('%s.data = self.%s;'%(v,m.name))
				sw.writeln('[%s unmarshall:bar];'%(v))
		else:
			sw.writeln('[self.%s unmarshall:bar]; '%m.name)
	sw.scope_end()

	# sw.writeln('return true;')
	# sw.scope_end().writeln(' // --  end function -- ')	# end function
	sw.wln()
	sw.writeln('@end')
	# sw.scope_end() # end class


def createCodeSequence(e,sw,idt):
	module = e.container
	sw.setstream(H_FILE)
	sw.wln()
	sw.resetVariant()
	sw.writeln('@interface %shlp:NSObject'%e.getName()).idt_inc()

	sw.writeln('@property NSMutableArray* data;')
	sw.wln()
	sw.writeln('-(void) marshall:(RpcByteArray*)bar;')
	sw.writeln('-(void) unmarshall:(RpcByteArray*)bar;')

	sw.idt_dec().writeln('@end')

	sw.setstream(MM_FILE)
	sw.wln()
	sw.writeln('@implementation %shlp'%e.getName())
	sw.wln()
	sw.writeln('-(id)init{').idt_inc()
	sw.writeln('self =[super init];')
	sw.writeln('self.data = [NSMutableArray init];')
	sw.writeln('return self;')
	sw.scope_end().wln()
	sw.writeln('-(void) marshall:(RpcByteArray*)bar{').idt_inc()
	sw.writeln('[bar writeUInt32:(uint32_t)[self.data count]];')
	sw.writeln('for(uint32_t n=0;n< (uint32_t)[self.data count];n++){').idt_inc()
	v = sw.newVariant('v')
	if Builtin.isBuiltinType(e.type.name):
		sw.define_var(v,e.type.getMappingTypeName2(module),'nil')
	else:
		sw.define_var(v,e.type.getMappingTypeName(module),'nil')
	sw.writeln('%s = [self.data objectAtIndex:n];'%v)
	if isinstance( e.type,Builtin):
		Builtin_Python.serial2(e.type,v,sw,'bar')
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		impled = False
		if isinstance(e.type,Sequence):
			if e.type.type.name == 'byte':
				# sw.writeln('[bar writeUInt32:[%s length]];'%v)
				sw.writeln('[bar writeData:%s];'%v) # v: NSData*


				# sw.writeln('d.writeInt(item.length);')
				# sw.writeln('d.write(item,0,item.length);')
				impled = True
		if not impled:
			v2 = sw.newVariant('v')
			sw.define_var(v2,'%shlp*'%e.type.name,'[%shlp new]'%(e.type.name) )
			sw.writeln('%s.data = %s;'%(v2,v))
			sw.writeln('[%s marshall:bar];'%v2)
			# sw.define_var(v,'%shlp'%e.type.name,'new %shlp(item)'%(e.type.name) )
			# sw.writeln('%s.marshall(d);'%v)
			# sw.writeln('[%s marshall:bar];'%v)
	else:
		# sw.writeln("item.marshall(d);")
		sw.writeln("[%s marshall:bar];"%v)

	sw.scope_end()
	#--- end for ----
	sw.scope_end()
	sw.wln()
	# sw.idt_dec().writeln('@end').wln()

	#-- unmarshall()
	sw.resetVariant()
	sw.writeln('-(void)unmarshall:(RpcByteArray*)bar{').idt_inc()

	vsize = sw.newVariant('size')
	sw.define_var(vsize,'uint32_t')
	sw.writeln('%s = [bar readUInt32];'%vsize)

	v = sw.newVariant('v')
	sw.writeln('for(uint32_t n=0;n<%s;n++){'%vsize).idt_inc()
	# sw.define_var(v,e.type.getMappingTypeName(module),'nil')
	if Builtin.isBuiltinType(e.type.name):
		sw.define_var(v,e.type.getMappingTypeName2(module),'nil')
	else:
		sw.define_var(v,e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module)  )
	if isinstance(e.type,Builtin): #无法包装直接的原始数据数组
		Builtin_Python.unserial2(e.type,v,sw,'bar')
		# sw.writeln("this.ds.add(_o);")
	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):
		impled = False
		if isinstance(e.type,Sequence):
			if e.type.type.name == 'byte':
				size = sw.newVariant('size')
				bf = sw.newVariant('_bf')
				# sw.writeln('uint32_t %s = [bar readUInt32];'%(size))
				# sw.writeln('%s = [bar readData:%s];'%(v,size))
				sw.writeln('%s = [bar readData];'%v)

				# sw.writeln('int %s = d.getInt();'%(size))
				# sw.writeln('byte[] %s = new byte[%s];'%(bf,size))
				# sw.writeln('d.get(%s);'%bf)
				# sw.writeln('this.ds.add(%s);'%bf)
				impled = True

		if not impled:
			# sw.define_var(v,e.type.getMappingTypeName(module),e.type.getTypeDefaultValue(module) )
			c = sw.newVariant('c')
			sw.define_var(c,"%shlp*"%e.type.name,"[%shlp new]"%(e.type.name))
			sw.writeln('%s.data = %s;'%(c,v))
			sw.writeln('[%s unmarshall:bar];'%c)
			# sw.define_var(c,"%shlp"%e.type.name,"new %shlp(%s)"%(e.type.name,v))
			# sw.writeln("%s.unmarshall(d);"%(c))
			# sw.writeln("this.ds.add(%s);"%v)
	else:
		sw.writeln('[%s unmarshall:bar];'%v)
		# sw.define_var(v,e.type.name,"new %s()"%e.type.name)
		# sw.writeln("%s.unmarshall(d);"%v)
		# sw.writeln("this.ds.add(%s);"%v)

	sw.writeln('[self.data addObject:%s];'%v)
	sw.scope_end()
	# -- end for --

	sw.scope_end()
	sw.wln()
	sw.idt_dec().writeln('@end').wln()



def createCodeDictionary(e,sw,idt):
	'''
		<key,val> key 必须是 builtin内建类型
	'''
	if True:
		module = e.container

		sw.setstream(H_FILE)
		sw.wln()

		# sw.writeln('import %s.*;'%(sw.pkg_current()) )
		# for ref in module.ref_modules.keys():
		# 	if sw.pkg_current()!=ref:
		# 		sw.writeln('import %s;'%ref)
		#
		# sw.writeln('import tce.*;')
		# sw.writeln('import java.util.*;')
		# sw.writeln('import java.io.*;')
		# sw.writeln('import java.nio.*;')
		# sw.wln()

		sw.writeln('@interface %shlp:NSObject'%e.getName()).idt_inc()
		sw.writeln('@property NSMutableDictionary* data;')
		sw.wln()
		sw.writeln('-(void) marshall:(RpcByteArray*)bar;')
		sw.writeln('-(void) unmarshall:(RpcByteArray*)bar;')
		sw.idt_dec().writeln('@end')
		# -- mm file
		sw.setstream(MM_FILE)
		sw.wln()
		sw.writeln('@implementation %shlp'%e.getName()).wln()
		sw.writeln('-(id)init{').idt_inc()
		sw.writeln('self =[super init];')
		sw.writeln('self.data = [NSMutableDictionary init];')
		sw.writeln('return self;')
		sw.scope_end().wln()

		# sw.writeln('public class %shlp {'%e.getName() ).idt_inc()
		# sw.writeln('//# -- THIS IS DICTIONARY! --')
		# sw.writeln('public %s ds = null;'%(e.getMappingTypeName(module))).wln()
		# sw.writeln('public %shlp(%s ds){'%(e.name,e.getMappingTypeName(module)) ).idt_inc()	#将hash数据{}传递进来
		# sw.writeln('this.ds = ds;')
		# sw.scope_end()
		# sw.wln()

		sw.resetVariant()
		# -- FUNCTION marshall()  BEGIN --
		sw.writeln('-(void) marshall:(RpcByteArray*)bar{').idt_inc()
		sw.writeln('[bar writeUInt32:(uint32_t)[self.data count]];')
		# sw.writeln('for(uint32_t n=0;n< (uint32_t)[self.data count];n++){').idt_inc()
		k = sw.newVariant('k')
		v = sw.newVariant('v')
		sw.writeln('NSEnumerator * enumerator = [self.data keyEnumerator];')

		# key 必须是内建builtin 类型
		sw.define_var(k,e.first.getMappingTypeName2(module))
		if isinstance(e.second,Builtin):
			sw.define_var(v,e.second.getMappingTypeName2(module))
		else:
			sw.define_var(v,e.second.getMappingTypeName(module))

		sw.writeln('while(true){').idt_inc()
		sw.writeln('%s = [enumerator nextObject];'%k)
		sw.writeln('if(%s == nil) break;'%k)
		sw.writeln('%s = [self.data objectForKey:%s ];'%(v,k))

		if isinstance( e.first,Builtin):
			Builtin_Python.serial2(e.first,k,sw,'bar')
		elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'error: <KEY> in dictionary not be in [sequence,dictionary]!'
			sys.exit(0)
			#key不支持符合数据类型，只能是简单数据类型(Builtin Types)
		else:
			sw.writeln("[%s marshall:bar];"%k)
		# do value
		if isinstance( e.second,Builtin):
			Builtin_Python.serial2(e.second,v,sw,'bar')
#			sw.scope_end()
		elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
			impled = False
			if isinstance( e.second,Sequence):
				if e.second.type.name == 'byte':
					# sw.writeln('[bar writeUInt32:[%s length]];'%v)
					sw.writeln('[bar writeData:%s];'%v)
					# sw.writeln('d.writeInt(%s.length);'%v)
					# sw.writeln('d.write(%s,0,%s.length);'%(v,v))
					impled = True

			if not impled:
				c = sw.newVariant('c')
				sw.define_var(c,'%shlp*'%e.second.name,'[%shlp new]'%(e.second.name) )
				sw.writeln('%s.data = %s;'%(c,v))
				sw.writeln('[%s marshall:bar];'%c)
		else:
			sw.writeln("[%s marshall:bar];"%v)
		sw.scope_end() # end while

		sw.scope_end() # end function
		sw.wln()

		#--	 FUNCTION  unmarshall() BEGIN --
		# sw.writeln("// unmarshall()")
		sw.resetVariant()
		sw.writeln('-(void)unmarshall:(RpcByteArray*)bar{').idt_inc()
		vsize = sw.newVariant('size')
		sw.define_var(vsize,'uint32_t')
		sw.writeln('%s = [bar readUInt32];'%vsize)

		# sw.writeln('public boolean unmarshall(ByteBuffer d){').idt_inc()
		# vsize = sw.newVariant('_size')
		# sw.writeln('int %s = 0;'%vsize)
		#
		# sw.writeln('try{').idt_inc()
		# sw.writeln('%s = d.getInt();'%vsize)

		sw.writeln('NSArray* keys = [self.data allKeys];')
		sw.writeln('for(uint32_t n=0;n< (uint32_t)[keys count];n++){').idt_inc()

		# sw.writeln("for(uint32 n=0;_p < %s;_p++){"%vsize).idt_inc()
		# k = sw.newVariant('_k')
		# v = sw.newVariant('_v')
		# c = sw.newVariant('c')

		sw.define_var(k,e.first.getMappingTypeName2(module),'nil' )

		if isinstance(e.first,Builtin):
			Builtin_Python.unserial2(e.first,k,sw,'bar')
		elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
			print 'error: <KEY> in dictionary not be in [sequence,dictionary]!'
			sys.exit(0)
		else:
			sw.writeln('[%s unmarshall:bar];'%k)

		c = sw.newVariant('c')
		if isinstance(e.second,Builtin):
			sw.define_var(v,e.second.getMappingTypeName2(module),'nil' )
		else:
			sw.define_var(v,e.second.getMappingTypeName(module),e.second.getTypeDefaultValue(module) )

		if isinstance(e.second,Builtin):
			Builtin_Python.unserial(e.second,v,sw,'bar')
		elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
			impled = False
			if isinstance(e.second,Sequence):
				if e.second.type.name == 'byte':
					size = sw.newVariant('size')
					# sw.writeln('%s = [bar readUInt32];'%size)
					# sw.writeln('%s = [bar readData:%s];'%(v,size))
					sw.writeln('%s = [bar readData];'%v)

					# bf = sw.newVariant('_bf')
					# sw.writeln('int %s = d.getInt();'%(size))
					# sw.writeln('%s = new byte[%s];'%(v,size))
					# sw.writeln('d.get(%s);'%v)

					impled = True

			if not impled:
				sw.define_var(c,'%shlp*'%e.second.name,'[%shlp new]'%(e.second.name))
				sw.writeln('%s.data = %s;'%(c,v))
				sw.writeln('[%s unmarshall:bar];'%(c))
		else:
			sw.writeln('[%s unmarshall:bar];'%v)

		sw.writeln('[self.data setObject:%s forKey:%s];'%(v,k))
		# sw.writeln("this.ds.put(%s,%s);"%(k,v))
		sw.scope_end() # end for

		# sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		# sw.writeln('return false;')
		# sw.scope_end() # end try{}
		#
		# sw.wln()
		#
		#
		# sw.writeln('return true;')
		# sw.scope_end()	# end function

		sw.scope_end() # end class
		# sw.writeln('//-- end Dictonary Class definations --')
		sw.writeln('@end')
		sw.wln()


def createProxy(e,sw,ifidx):
	# 创建代理
	module = e.container

	sw.setstream(H_FILE).wln()

	# sw.classfile_enter('%sProxy'%e.getName())
	# sw.wln()

	# sw.writeln('import tce.*;')
	# sw.writeln('import java.io.*;')
	# sw.writeln('import java.nio.*;')
	# sw.writeln('import java.util.*;')
	# sw.wln()

	#	sw.writeln("import %s.%s;"%(sw.pkg_current(), e.getName() ) )
	# sw.wln()
	sw.writeln('@interface %sProxy:RpcProxyBase'%e.getName() ).idt_inc()
	sw.writeln('+(id)createWithConnection:(RpcConnection*)conn;')
	sw.writeln('+(id)createWithInetAddressHost:(NSString*)host andPort:(int)port;')
	sw.writeln('+(id)createWithProxy:(RpcProxyBase*)proxy;')
	sw.writeln('-(void)destroy;')

	for opidx,m in enumerate(e.list): # function list
		opidx = m.index

		sw.wln()
		#		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象
		list =[]
		for n  in range(len(m.params)):
			p = m.params[n]
			if n!=0:
				list.append('%s:(%s)%s'%(p.id,p.type.getMappingTypeName(module),p.id) )
			else:
				list.append('(%s)%s'%(p.type.getMappingTypeName(module),p.id) )
		ss = string.join( list,' ')
		if ss: ss = ':'+ss

		# 函数定义开始
		if m.type.name == 'void': # oneway call
			if len(m.params) == 0:
				sw.writeln('-(void) %s_oneway:(NSDictionary*)props;'%(m.name) )
			else:
				sw.writeln('-(void) %s_oneway%s props:(NSDictionary*)props;'%(m.name,ss) )

		# sw.writeln('-(%s)%s_async%s props:(NSDictionary*)props cookie:(id)cookie;'%(m.type.getMappingTypeName(module)),m.name,s)
		retparam='void (^)(RpcProxyBase* proxy,id cookie)' #
		if m.type.name!='void':
			retparam='void (^)(%s result,RpcProxyBase* proxy,id cookie)'%m.type.getMappingTypeName(module)
		if len(m.params) == 0:
			sw.writeln('-(void)%s_async:(%s)succ error:(void (^)(int error,RpcProxyBase* proxy,id cookie) )error props:(NSDictionary*)props cookie:(id)cookie;'%(m.name,retparam))
		else:
			sw.writeln('-(void)%s_async%s async:(%s)succ error:(void (^)(int error,RpcProxyBase* proxy,id cookie))error props:(NSDictionary*)props cookie:(id)cookie;'%(m.name,ss,retparam))

	#-- end create()
	sw.idt_dec().wln()
	sw.writeln('@end')



	sw.setstream(MM_FILE)
	sw.wln()
	sw.resetVariant()
	#-- begin destroy()
	sw.writeln('@implementation %sProxy'%e.getName()).wln()

	sw.writeln('-(void)destroy{').idt_inc()
	sw.writeln('[self.conn close];')
	sw.scope_end()
	#-- end destroy()
	sw.wln()
	sw.writeln('+(id)createWithConnection:(RpcConnection*)conn{').idt_inc()
	sw.writeln('%sProxy * prx = [%sProxy new];'%(e.getName(),e.getName()))
	sw.writeln('prx.conn = conn;')
	sw.writeln('return prx;')
	sw.scope_end()
	sw.wln()
	sw.writeln('+(id)createWithInetAddressHost:(NSString*)host andPort:(int)port{').idt_inc()
	sw.writeln('RpcConnection* conn = [[RpcCommunicator instance] createConnection:host port:port];')
	sw.writeln('return [%sProxy createWithConnection:conn];'%e.getName() )
	sw.scope_end()
	sw.wln()
	sw.writeln('+(id)createWithProxy:(RpcProxyBase*)other{').idt_inc()
	sw.writeln('%sProxy * prx = [%sProxy new];'%(e.getName(),e.getName()))
	sw.writeln('prx.conn = other.conn;')
	sw.writeln('return prx;')
	sw.scope_end()

	#-- member funtion list --
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index

		sw.wln()
		list =[]
		for n  in range(len(m.params)):
			p = m.params[n]
			if n!=0:
				list.append('%s:(%s)%s'%(p.id,p.type.getMappingTypeName(module),p.id) )
			else:
				list.append('(%s)%s'%(p.type.getMappingTypeName(module),p.id) )
		ss = string.join( list,' ')
		if ss: ss = ':'+ss
		# 函数定义开始
		sw.resetVariant()
		if m.type.name == 'void': # oneway call
			if len(m.params) ==0:
				sw.writeln('-(void) %s_oneway:(NSDictionary*)props{'%(m.name)).idt_inc()
			else:
				sw.writeln('-(void) %s_oneway%s props:(NSDictionary*)props{'%(m.name,ss)).idt_inc()

			m1 = sw.newVariant('m')
			v = sw.newVariant('v')
			sw.writeln('NSMutableDictionary* %s = [NSMutableDictionary new];'%v)
			sw.writeln('[%s setDictionary:%s];'%(v,'props'))
			sw.define_var(m1,'RpcMessage*','[[RpcMessage alloc] initWithCallType:RpcMsgCallType_CALL]')
			sw.writeln('%s.ifidx = %s;'%(m1,ifidx))
			sw.writeln('%s.opidx = %s;'%(m1,opidx))
			sw.writeln('%s.paramsize = %s;'%(m1,len(m.params)))
			sw.writeln('[%s.extra setProperties:%s];'%(m1,v))
			if len(m.params):
				sw.writeln('%s.content = [RpcByteArray new];'%(m1))
			for p in m.params:
				if isinstance(p.type,Builtin):
					Builtin_Python.serial(p.type,p.id,sw,'%s.content'%m1)
				elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
					impled = False
					if p.type.type.name == 'byte':
						sw.writeln('[%s.content writeData:%s];'%(m1,p.id))
						impled = True
					if not impled:
						c = sw.newVariant('c')
						sw.define_var(c,'%shlp*'%p.type.name,'[%shlp new]'%(p.type.name))
						sw.writeln('[%s marshall:%s.content];'%(c,m1))
				else:
					sw.writeln("[%s marshall:%s.content];"%(p.id,m1))
			sw.writeln('%s.proxy = self;'%m1)
			sw.writeln('[self.conn sendMessage:%s];'%m1)
			sw.scope_end()
		sw.wln()
		# asynchronized call

		# list =[]
		# for n  in range(len(m.params)):
		# 	p = m.params[n]
		# 	list.append('%s:(%s)%s'%(p.id,p.type.getMappingTypeName(module),p.id) )
		# ss = string.join( list,' ')
		# if ss: ss = ':'+ss
		# sw.writeln('-(void)%s_async%s async:(%s_AsyncCallBack*)async props:(NSDictionary*)props cookie:(id)cookie;'%(m.type.getMappingTypeName(module)),m.name,ss).idt_inc()

		retparam='void (^)(RpcProxyBase* proxy,id cookie)' #
		if m.type.name!='void':
			retparam='void (^)(%s result,RpcProxyBase* proxy,id cookie)'%m.type.getMappingTypeName(module)
		if len(m.params) == 0:
			sw.writeln('-(void)%s_async:(%s)succ error:(void (^)(int error,RpcProxyBase* proxy,id cookie) )error props:(NSDictionary*)props cookie:(id)cookie{'%(m.name,retparam)).idt_inc()
		else:
			sw.writeln('-(void)%s_async%s async:(%s)succ error:(void (^)(int error,RpcProxyBase* proxy,id cookie))error props:(NSDictionary*)props cookie:(id)cookie{'%(m.name,ss,retparam)).idt_inc()


		m1 = sw.newVariant('m')
		v = sw.newVariant('v')
		sw.writeln('NSMutableDictionary* %s = [NSMutableDictionary new];'%v)
		sw.writeln('[%s setDictionary:%s];'%(v,'props'))
		sw.define_var(m1,'RpcMessage*','[[RpcMessage alloc] initWithCallType:RpcMsgCallType_CALL]')
		sw.writeln('%s.ifidx = %s;'%(m1,ifidx))
		sw.writeln('%s.opidx = %s;'%(m1,opidx))
		sw.writeln('%s.paramsize = %s;'%(m1,len(m.params)))
		sw.writeln('[%s.extra setProperties:%s];'%(m1,v))
		sw.writeln('%s.cookie = cookie;'%m1)
		if len(m.params):
			sw.writeln('%s.content = [RpcByteArray new];'%(m1))
		for p in m.params:
			if isinstance(p.type,Builtin):
				Builtin_Python.serial(p.type,p.id,sw,'%s.content'%m1)
			elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
				impled = False
				if p.type.type.name == 'byte':
					sw.writeln('[%s.content writeData:%s];'%(m1,p.id))
					impled = True
				if not impled:
					c = sw.newVariant('c')
					sw.define_var(c,'%shlp*'%p.type.name,'[%shlp new]'%(p.type.name))
					sw.writeln('%s.data = %s;'%(c,p.id))
					sw.writeln('[%s marshall:%s.content];'%(c,m1))
			else:
				sw.writeln("[%s marshall:%s.content];"%(p.id,m1))
		sw.writeln('%s.proxy = self;'%m1)
		sw.writeln('%s.async = [%s_AsyncCallBack new];'%(m1,e.getName()))
		sw.writeln('[%s.async setOnSucc:succ];'%m1)
		sw.writeln('[%s.async setOnError:error];'%m1) 		#设置回调通知函数
		sw.writeln('[self.conn sendMessage:%s];'%m1)
		sw.scope_end()

	# sw.scope_end() # end class PROXY class END --  '}'
	# sw.classfile_leave()
	sw.writeln('@end')
	#---------------定义 异步调用 基类  --------------------
	# sw.setstream(MM_FILE)
	# sw.wln()
	# sw.resetVariant()

	sw.setstream(H_FILE)
	sw.wln()
	sw.resetVariant()
	sw.writeln('@interface %s_AsyncCallBack:RpcAsyncCallBackBase'%e.getName() ).idt_inc()
	sw.writeln('-(void) callReturn:(RpcMessage*)m1 m2:(RpcMessage*)m2;')
	sw.wln().idt_dec().writeln('@end')

	sw.setstream(MM_FILE)
	sw.wln()
	sw.resetVariant()
	sw.writeln('@implementation %s_AsyncCallBack'%e.getName())
	sw.wln()
	sw.writeln('-(void) callReturn:(RpcMessage*)m1 m2:(RpcMessage*)m2{').idt_inc()

	for opidx,m in enumerate(e.list):
		opidx = m.index
		v = sw.newVariant('v')
		fx = sw.newVariant('fx')
		sw.writeln('if(m1.opidx == %s){'%opidx).idt_inc()
		sw.writeln('if( m2.errcode !=RPCERROR_SUCC){').idt_inc()
		sw.writeln('void (^%s)(int error,RpcProxyBase* proxy,id cookie) = self.onError;'%fx)
		sw.writeln('%s(m2.errcode,m1.proxy,m1.cookie);'%fx)
		sw.writeln('return;')
		sw.scope_end()

		if m.type.name =='void':
			fx = sw.newVariant('fx')
			sw.writeln('void (^%s)(RpcProxyBase* proxy,id cookie) = self.onSucc;'%fx)
			sw.writeln('%s(m1.proxy,m1.cookie);'%fx)
		else:
			v = sw.newVariant('cr')
			sw.define_var(v,m.type.getMappingTypeName(module),m.type.getTypeDefaultValue(module))
			if isinstance(m.type,Builtin):
				Builtin_Python.unserial(m.type,v,sw,'m2.content')
			elif isinstance(m.type,Sequence)  or isinstance(m.type,Dictionary):
	#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())
				impled = False
				if isinstance(m.type,Sequence):
					if m.type.type.name == 'byte':
						sw.writeln('%s = [m2.content readData];'%v)
						impled = True
				if not impled:
					c = sw.newVariant('c')
					sw.define_var(c,'%shlp*'%m.type.name,'[%shlp new]'%(m.type.name))
					sw.writeln('%s.data = %s;'%(c,v))
					sw.writeln('[%s unmarshall: m2.content];'%c)
		#			sw.writeln('%s(%s,%s);'%(m.name,v,'m1.prx')) # 不考虑unmarshall()是否okay

			else:
	#			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%m.type.getMappingTypeName())
				sw.writeln('[%s unmarshall: m2.content];'%v)
				# sw.writeln('r = %s.unmarshall(d);'%v)
			# sw.writeln('%s(%s,%s,%s);'%(m.name,v,'m1.prx','m1.cookie')) #不考虑unmarshall是否okay
			fx = sw.newVariant('fx')
			sw.writeln('void (^%s)(%s result,RpcProxyBase* proxy,id cookie) = self.onSucc;'%(fx,m.type.getMappingTypeName(module)))
			sw.writeln('%s(%s,m1.proxy,m1.cookie);'%(fx,v))

		sw.scope_end() # end if
	sw.scope_end() # end funcion callReturn()

	sw.writeln('@end')


interface_defs={}
ifcnt = 0

fileifx = open('ifxdef.txt','w') #接口表文件

def createCodeInterface(e,sw,idt,idx):
	global  interface_defs,ifcnt

	ifidx = ifcnt
	ifcnt+=1
	# ifidx = e.ifidx #过滤之后的接口索引( 暂停 )
	module = e.container
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

	fileifx.write('<if id="%s" name="%s.%s"/>\n'%(ifidx,module.name,e.name))
	fileifx.flush()

	tce_util.rebuildFunctionIndex(e)

	interface_defs[ifidx] = {'e':e,'f':{}}

	createProxy(e,sw,ifidx)

	# if not e.delegate_exposed: #是否暴露委托对象,如果需要本地接收远程RPC请求则需要定义filter
	# 	return
	expose = tce_util.isExposeDelegateOfInterfaceWithName(ifname)
	if not expose:
		return

	sw.setstream(H_FILE)
	sw.wln()
	sw.resetVariant()
	sw.writeln('@class %s_delegate;'%e.getName())
	sw.writeln('@interface %s : RpcServant'%e.getName()).idt_inc()
	sw.wln()
	sw.writeln('@property %s_delegate * delegate;'%e.getName() )
	for m in e.list: # function list
		params=[]
		for n in range(len(m.params)):
			p = m.params[n]
			if n!=0:
				params.append('%s:(%s)%s'%(p.id,p.type.getMappingTypeName(module),p.id))
			else:
				params.append( '(%s)%s'%(p.type.getMappingTypeName(module),p.id) )
		ss = string.join( params,' ')
		if ss: ss =':'+ ss +' context:'
		else: ss = ':'
		sw.writeln('-(%s) %s%s(RpcContext*)ctx;'%(m.type.getMappingTypeName(module),m.name,ss))
	sw.wln().idt_dec().writeln('@end')

	sw.setstream(MM_FILE)
	sw.wln()
	sw.resetVariant()
	sw.writeln('@implementation %s'%e.getName())
	sw.wln()
	sw.writeln('-(id) init{').idt_inc()
	sw.writeln('self = [super init];')
	sw.writeln('self.delegate = [%s_delegate new];'%e.getName())
	sw.writeln('self.delegate.servant = self;')
	sw.writeln('return self;')
	sw.scope_end()

	sw.wln()
	sw.writeln('-(RpcServantDelegate*) getDelegate{').idt_inc()
	sw.writeln('return self.delegate;')
	sw.scope_end()

	#定义servant 接口函数
	for m in e.list: # function list
		sw.wln()
		params=[]
		for n in range(len(m.params)):
			p = m.params[n]
			if n!=0:
				params.append('%s:(%s)%s'%(p.id,p.type.getMappingTypeName(module),p.id))
			else:
				params.append( '(%s)%s'%(p.type.getMappingTypeName(module),p.id) )
		ss = string.join( params,' ')
		if ss: ss =':'+ ss +' context:'
		else: ss = ':'

		sw.writeln('-(%s) %s%s(RpcContext*)ctx{'%(m.type.getMappingTypeName(module),m.name,ss)).idt_inc()

		if isinstance( m.type ,Builtin ):
			if m.type.name =='void':
				sw.scope_end()
				continue
			else:
				sw.writeln("return %s;"%m.type.getTypeDefaultValue(module))
		elif isinstance(m.type,Sequence):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(module) )
		elif isinstance(m.type,Dictionary):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(module) )
		else:
			sw.writeln("return %s;"%m.type.getTypeDefaultValue(module) )
		sw.scope_end()

	sw.wln().writeln('@end')

	#begin delegate() ----
	sw.setstream(H_FILE)
	sw.wln()

	sw.writeln('@interface %s_delegate:RpcServantDelegate'%e.getName()).idt_inc()
	# sw.writeln("public class %s_delegate extends RpcServantDelegate {"%e.getName()).idt_inc()
	sw.wln()
	sw.writeln('@property %s servant;'%e.getTypeName(module))

	#实现invoke()接口
	sw.wln()
	sw.writeln('-(void) invoke:(RpcMessage*)m;')
	sw.wln()
	sw.idt_dec()
	sw.writeln('@end')

	sw.setstream(MM_FILE)
	sw.resetVariant()
	sw.wln()
	sw.writeln('@implementation %s_delegate'%e.getName())
	sw.wln()
	sw.writeln('-(id) init{').idt_inc()
	sw.writeln('self=[super init];')
	sw.writeln('self.ifidx = %s;'%ifidx)
	sw.writeln('return self;')
	sw.scope_end().wln()

	sw.writeln('-(void) invoke:(RpcMessage*)m{').idt_inc()

	for opidx,m in enumerate(e.list):
		opidx = m.index
		sw.writeln('if(m.opidx == %s ){'%opidx).idt_inc()
		sw.writeln('[self func_%s_delegate:m];'%m.name )
		sw.scope_end()
	sw.scope_end()

	#开始委托 函数定义
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		# sw.writeln('boolean func_%s_delegate(RpcMessage m){'%(m.name) ).idt_inc()
		sw.wln()
		sw.resetVariant()
		m1 = sw.newVariant('m1')
		sw.writeln('-(void)func_%s_delegate:(RpcMessage*)%s{'%(m.name,m1) ).idt_inc()

		params=[ ]
		if m.params:
			# sw.writeln('RpcByteArray* bar =[RpcByteArray new];')
			sw.writeln('RpcByteArray* bar = %s.content;'%m1)
		for p in m.params:
			if isinstance(p.type,Builtin):
				sw.define_var(p.id,p.type.getMappingTypeName(module))
				Builtin_Python.unserial(p.type,p.id,sw,'bar')
			elif isinstance(p.type,Sequence)  or isinstance(p.type,Dictionary):
				impled = False
				#print p.type,p.type.type.name
				if isinstance(p.type,Sequence):
					if p.type.type.name == 'byte':
						sw.define_var(p.id,p.type.getMappingTypeName(module),p.type.getTypeDefaultValue(module))
						sw.writeln('%s = [bar readData];'%p.id)
						impled = True

				if not impled:
					sw.define_var(p.id,p.type.getMappingTypeName(module),p.type.getTypeDefaultValue(module))
					c = sw.newVariant('c')
					sw.define_var(c,'%shlp*'%p.type.name,'[%shlp new]'%(p.type.name))
					sw.writeln('%s.data = %s;'%(c,p.id))
					sw.writeln('[%s unmarshall: bar];'%c)

			else:
				sw.define_var(p.id,p.type.getMappingTypeName(module),p.type.getTypeDefaultValue(module))
				sw.writeln('[%s unmarshall:bar];'%p.id)

			params.append(p.id)
		#params = map( lambda x: '_p_'+x,params)

		list =[]
		for n  in range(len(m.params)):
			p = m.params[n]
			if n!=0:
				list.append('%s:%s'%(p.id,p.id) )
			else:
				list.append('%s'%(p.id) )
		ss = string.join( list,' ')
		# if ss:
		# 	ss+=' context:ctx'
		# else:
		# 	ss+=':ctx'
		if ss: ss =':'+ ss +' context:'
		else: ss = ':'


		succ = sw.newVariant('succ')
		sw.define_var(succ,'int','RPCERROR_SUCC');

		cr = 'undefined'
		sw.writeln('RpcContext* ctx = [RpcContext new];')
		sw.writeln('ctx.msg = %s;'%m1)

		if m.type.name !='void': # none return value
			cr = sw.newVariant('cr')
			sw.define_var(cr,m.type.getMappingTypeName(module))

		sw.writeln('@try{').idt_inc()
		if isinstance(m.type,Builtin) and m.type.type =='void': # none return value
			sw.writeln("[self.servant %s%sctx];"%(m.name,ss) )
		else:
			sw.writeln("%s = [self.servant %s%sctx];"%(cr,m.name,ss) )
		sw.idt_dec().writeln('} @catch(NSException *exception){').idt_inc()
		sw.writeln('%s=RPCERROR_REMOTEMETHOD_EXCEPTION;'%succ)
		sw.writeln('NSLog(@"%@",exception);')
		sw.scope_end()

		#--单向调用，并无返回
		sw.writeln("if( (%s.calltype & RpcMsgCallType_ONEWAY) !=0 ){"%m1).idt_inc()
		sw.writeln("return ;") #异步调用不返回等待
		sw.scope_end()

		sw.wln()
		#处理返回值
		# sw.writeln('if(%s == nil){'%cr).idt_inc()
		# sw.writeln('%s = %s;'%(cr,m.type.getTypeDefaultValue(module)))
		# sw.scope_end()

		if True:
		# if m.type.name !='void':
			m2 = sw.newVariant('m2')
			sw.define_var(m2,'RpcMessage*','[[RpcMessage alloc] initWithCallType: RpcMsgCallType_RETURN]')
			sw.writeln('%s.sequence = %s.sequence;'%(m2,m1))
			sw.writeln('%s.callmsg = %s;'%(m2,m1))
			sw.writeln('%s.conn = %s.conn;'%(m2,m1))
			sw.writeln('%s.ifidx = %s.ifidx;'%(m2,m1))
			sw.writeln('%s.call_id = %s.call_id;'%(m2,m1))
			sw.writeln('%s.errcode = %s;'%(m2,succ))
			v = sw.newVariant('temp')
			sw.writeln('NSString* %s = [%s.extra.properties objectForKey:@"__user_id__"];'%(v,m1))
			sw.writeln('if( %s !=nil){'%v).idt_inc()
			sw.writeln('[%s.extra.properties setObject: %s forKey:@"__user_id__"];'%(m2,v))
			# sw.writeln('if(m.extra.getProperties().containsKey("__user_id__")){').idt_inc()
			# sw.writeln('mr.extra.setPropertyValue("__user_id__",m.extra.getPropertyValue("__user_id__"));')
			sw.scope_end()

			sw.writeln('if(%s.errcode !=RPCERROR_SUCC){'%m2).idt_inc()
			sw.writeln("[%s.conn sendMessage:%s];"%(m1,m2))
			sw.writeln('return ;')
			sw.scope_end()

			if m.type.name !='void':
		#		sw.writeln("m.sequence = ctx.msg.sequence;") #返回事务号与请求事务号必须一致
				# 返回值序列化
				bar = sw.newVariant('bar')
				sw.writeln('RpcByteArray* %s=[RpcByteArray new];'%bar)
				if isinstance( m.type ,Builtin ) and m.type.name!='void':
					Builtin_Python.serial(m.type,cr,sw,bar)
				elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
					impled = False
					if isinstance(m.type,Sequence):
						if m.type.type.name == 'byte':
							sw.writeln('[%s writeData:%s];'%(bar,cr))
							# sw.writeln('%s.writeInt(%s.length);'%('dos','cr'))
							# sw.writeln('%s.write(%s,0,%s.length);'%('dos','cr','cr'))
							impled = True
					if not impled:
						c = sw.newVariant('c')
						sw.define_var(c,'%shlp*'%m.type.name,'[%shlp new]'%m.type.name)
						sw.writeln('%s.data = %s;'%(c,cr) )
						sw.writeln('[%s marshall:%s];'%(c,bar))
				else:
					sw.writeln("[%s marshall:%s];"%(cr,bar) )
				sw.writeln('%s.paramsize = 1;'%m2)
				sw.writeln('%s.content = %s;'%(m2,bar))
			else:
				sw.writeln('%s.paramsize = 0;'%m2)
			sw.writeln("[%s.conn sendMessage:%s];"%(m1,m2))


		sw.scope_end() # end servant function{}
		# sw.wln()
	# sw.scope_end() # end fun_xxx_delegate

	# sw.scope_end() # end invoke() function --
	sw.wln()
	sw.writeln('@end')
	# sw.classfile_leave()
	return


# def createCodeInterfaceMapping():
# 	global interface_defs # {e,f:{}}
# 	pass
#



def createCodeFrame(e,idx,sw ):
	idt = Indent()
	txt=''
	# sw.setIncludes('default',(txt,))

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
#
#	createCodeInterfaceMapping() #创建 链接上接收的Rpc消息 根据其ifx编号分派到对应的接口和函数上去

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

	file = 'idl/main.idl'

	ostream = Outputer()
	#ostream.addHandler(sys.stdout)

	argv = sys.argv
	outdir = './output'
	pkgname = ''
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

		# if p == '-p':
		# 	if argv:
		# 		pkgname = argv.pop(0)

		if p =='-filter':
			if argv:
				filters = argv.pop(0)
	fp = None
	content = None
	try:
		fp = open(file,'r')
		content = fp.read()
		fp.close()
	except:
		print 'access file: %s failed!'%file
		sys.exit()

	if content.find('\n\r') ==-1:
		content.replace('\r','\n\r')

	if not os.path.exists(outdir):
		os.mkdir(outdir)

	import tce_util
	tce_util.getInterfaceIndexWithName('')
#	print outdir


	sw = StreamWriter()
	# name = os.path.basename(file).split('.')[0]
	# if not pkgname:
	# 	pkgname = name
#	print pkgname
	print file
	idlfiles = file.strip().split(',')
	for file in idlfiles:
		lexparser.curr_idl_path = os.path.dirname(file)
		parse_idlfile(file)


#	ostream.write(headtitles)
	unit = syntax_result()
	print global_modules_defs



	os.chdir( outdir )
	for module in global_modules:
		name = module.name
		print 'module:',name,module.ref_modules.keys()
		# print module.children

		sw = StreamWriter(ostream,Indent())
		sw.createPackage(name)
		# sw.pkg_enter(name)

		for idx,e in enumerate(module.list):
			createCodeFrame(e,idx,sw)

		sw.pkg_leave()

		# for ref in module.ref_modules.keys():
		# 	sw.writeln('import %s'%ref)



class LanguageObjc(object):
	language = 'csharp'
	class Builtin:
		@classmethod
		def defaultValue(cls,this):
			r = '@""'    #  as 'string'
			if this.type in ('byte','short','int','long','float','double'):
				r = '0'
			elif this.type == 'bool':
				r = 'false'
			return r

		@classmethod
		def typeName(cls,this):
			type = this.type
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
			return r

	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			if this.type.name == 'byte':
				return '[NSData new]'
			return '[NSMutableArray new]'

		@classmethod
		def typeName(cls,this,call_module):
			r = 'NSMutableArray*'
			if this.type.name == 'byte':
				r = 'NSData*'
			return r


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return '[NSMutableDictionary new]'


		@classmethod
		def typeName(cls,this,call_module):
			r = 'NSMutableDictionary*'
			return r


	class Struct:
		@classmethod
		def defaultValue(cls,this,call_module):
			return '[%s new]'%this.getTypeName(call_module).replace('*','')

		@classmethod
		def typeName(cls,this,call_module):
			return '%s *'%this.name


	class Module:
		def __init__(self,m):
			self.m = m



lexparser.language = 'objc'
lexparser.lang_kws = ['for', 'import', 'float', 'new', 'class', 'interface', 'extends', 'while', 'do', 'package', 'timeout', 'props']


lexparser.codecls = LanguageObjc

if __name__ =='__main__':
	createCodes()

"""
usage:
	tce2objc.py -i service.idl,.. -o output_dir

"""


