#--coding:utf-8--

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

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
		return self

	def dec(self,n=1):
		self.indents -=n
		if self.indents < 0 :
			self.reset()
		return self

	def reset(self):
		self.indents = 0
		return self

	def str(self):
		return '\t'*self.indents

	def __str__(self):
		return self.str()

NEWLINE = '\n'
CR = NEWLINE

class StreamWriter:
	def __init__(self,ostream,idt):
		self.ostream = ostream
		self.idt = idt
		self.lastvar =''
		self.varidx = 0

	def writeln(self,s,*s1):
		self.ostream.write(self.idt.str())
		self.ostream.write( str(s) )
		for s in s1:
			self.ostream.write( str(s))
		self.ostream.write(NEWLINE)
		return self

	def wln(self):
		return self.writeln('')

	def crlr(self):
		return self.wln()

	def idt_inc(self):
		self.idt.inc()
		return self

	def idt_dec(self):
		self.idt.dec()
		return self

	def newVariant(self,name):
		self.varidx +=1
		self.lastvar = "%s_%s"%(name,self.varidx)
		return self.lastvar

	def resetVariant(self):
		self.varidx = 0

class Builtin_Python:
	def __init__(self):
		pass

	@staticmethod
	def serial(typ,val,idt,stream='d'):
		# typ - builtin ; val - variant name
		s=''
		if typ == 'byte':
			# s = "%s += struct.pack('B',%s)"%(var,val)
			s = '%s = tce.serial_byte(%s,%s)'%(stream,val,stream)
		elif typ == 'bool':
			# s = "if %s == True:%s=1"%(val,val)+NEWLINE
			# s+=idt.str() +"else: %s=0"%(val)+NEWLINE
			# s+=idt.str() + "%s += struct.pack('B',%s)"%(var,val)
			s = '%s = tce.serial_bool(%s,%s)'%(stream,val,stream)
		elif typ == 'short':
			# s = "%s += struct.pack('!h',%s)"%(var,val)
			s = '%s = tce.serial_short(%s,%s)'%(stream,val,stream)
		elif typ == 'int':
			# s = "%s += struct.pack('!i',%s)"%(var,val)
			s = '%s += tce.serial_int(%s,%s)'%(stream,val,stream)
		elif typ == 'long':
			# s = "%s += struct.pack('!q',%s)"%(var,val)
			s = '%s = tce.serial_long(%s,%s)'%(stream,val,stream)
		elif typ in ('float',):
			# s = "%s += struct.pack('!f',%s)"%(var,val)
			s = '%s = tce.serial_float(%s,%s)'%(stream,val,stream)
		elif typ in ('double',):
			# s = "%s += struct.pack('!d',%s)"%(var,val)
			s = '%s = tce.serial_double(%s,%s)'%(stream,val,stream)
		elif typ =='string':
			# 添加4字节头 长度
			# s = "if type(%s) in (type(0),type(0.1)): %s=str(%s)"%(val,val,val) + CR + idt.str()
			# s+= "if not %s: %s=''"%(val,val) + NEWLINE+idt.str()
			# s+= 'try:' + NEWLINE +idt.inc().str()
			# s+= "%s = %s.encode('utf-8')"%(val,val) + NEWLINE + idt.dec().str()
			# s+= 'except:pass' + CR + idt.str()
			# s+= "%s += struct.pack('!I', len(str(%s)))"%(var,val)
			# s+= CR + idt.str() +  "%s += str(%s)"%(var,val)
			s = '%s = tce.serial_string(%s,%s)'%(stream,val,stream)
		return s

	@staticmethod
	def unserial(typ,val,stream,idt,idx='idx'):
		s=''
		funx = None
		if typ == 'byte':
			# s = "%s, = struct.unpack('B',%s[%s:%s+1])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + "%s+=1"%(idx)
			# s = '%s,%s = tce.unserial_byte(%s,%s)'%(val,idx,stream,idx)
			funx = 'tce.unserial_byte'
		elif typ == 'bool':
			# s = "%s, = struct.unpack('B',%s[%s:%s+1])"%(val,stream,idx,idx)
			# s+= NEWLINE +idt.str() + "if %s == 0: %s = False"%(val,val)
			# s+= NEWLINE +idt.str() + "else: %s = True"%(val)
			# s+= NEWLINE + idt.str() + "%s+=1"%idx

			# s = '%s,%s = tce.unserial_bool(%s,%s)'%(val,idx,stream,idx)
			funx = 'tce.unserial_bool'
		elif typ == 'short':
			# s = "%s, = struct.unpack('!h',%s[%s:%s+2])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + "%s+=2"%idx
			# s = '%s,%s = tce.unserial_short(%s,%s)'%(val,idx,stream,idx)
			funx = 'tce.unserial_short'
		elif typ == 'int':
			# s = "%s, = struct.unpack('!i',%s[%s:%s+4])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + "%s+=4"%idx
			# s = '%s,%s = tce.unserial_int(%s,%s)'%(val,idx,stream,idx)
			funx = 'tce.unserial_int'
		elif typ == 'long':
			# s = "%s, = struct.unpack('!q',%s[%s:%s+8])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + "%s+=8"%idx
			funx = 'tce.unserial_long'
		elif typ == 'float':
			# s = "%s, = struct.unpack('!f',%s[%s:%s+4])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + "%s+=4"%idx
			funx = 'tce.unserial_float'
		elif typ == 'double':
			# s = "%s, = struct.unpack('!d',%s[%s:%s+8])"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + '%s+=8'%idx
			funx = 'tce.unserial_double'
		elif typ =='string':
			#4 字节string长度
			# s = "__size, = struct.unpack('!I',%s[%s:%s+4])"%(stream,idx,idx)
			# s+=NEWLINE + idt.str() + '%s+=4'%idx
			# s+= NEWLINE + idt.str() + "%s = %s[%s:%s+__size]"%(val,stream,idx,idx)
			# s+= NEWLINE + idt.str() + '%s+=__size'%idx
			funx = 'tce.unserial_string'
		s = '%s,%s = %s(%s,%s)'%(val,idx,funx,stream,idx)
		return s


def createCodeStruct(module,e,ostream,idt):
	sw = StreamWriter(ostream,idt)

	params=[ ]
	for m in e.list:
		v = m.type.getTypeDefaultValue(module)
		params.append( (m.name,v) )
	pp =map(lambda x: '%s=%s'%(x[0],x[1]),params)
	ps = string.join(pp,',')
	l ='class %s:'%e.getName()
	sw.writeln(l)
	sw.writeln("# -- STRUCT -- ")
	sw.idt_inc()

	sw.writeln('def __init__(self,%s):'%(ps) )
	sw.idt_inc()
	for m in e.list:
		sw.writeln('self.%s = %s'%(m.name,m.name) )
	sw.writeln('')

	sw.idt_dec()


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

	sw.writeln('def marshall(self):')

	sw.idt_inc()
	sw.writeln("d =''")

	for m in e.list:
#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			s = Builtin_Python.serial(m.type.type,'self.' + m.name,idt)
			sw.writeln(s)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.writeln('container = %s(self.%s)'%(m.type.getTypeName(module),m.name) )
			sw.writeln('d += container.marshall()' )
		else:
			sw.writeln("d += self.%s.marshall()"% m.name )


	sw.writeln('return d')
	sw.writeln('')

	#unmarshall()
	sw.idt_dec()
	sw.writeln("def unmarshall(self,d,idx_=0):" )

	sw.idt_inc()
	sw.writeln('idx = idx_' )
	sw.writeln( "try:")

	sw.idt_inc()
	for m in e.list:

		if isinstance(m.type,Sequence) and m.type.type.name=='byte':
			s = Builtin_Python.unserial('string','self.' + m.name,'d' , idt,'idx')
			if s:
				sw.writeln(s)
		else:
			if isinstance(m.type,Builtin):
				s = Builtin_Python.unserial(m.type.type,'self.' + m.name,'d' , idt,'idx')
				if s:
					sw.writeln(s)
			elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
				if isinstance(m.type,Sequence):
					sw.writeln('self.%s = [ ]'%(m.name) )
				else:
					sw.writeln('self.%s = {}'%(m.name) )
				sw.writeln('container = %s(self.%s)'%(m.type.getTypeName(module),m.name) )
				sw.writeln('r,idx = container.unmarshall(d,idx)' )
				sw.writeln('if not r: return False,idx')
			else:
				sw.writeln('r,idx = self.%s.unmarshall(d,idx)'%m.name )
				sw.writeln('if not r: return False,idx')

	sw.idt_dec()
	sw.writeln('except:' )
	sw.idt_inc()
	sw.writeln('traceback.print_exc()' )
	sw.writeln('return False,idx' )

	sw.idt_dec()
	sw.writeln('return True,idx')
	sw.writeln('')


def createCodeSequence(e,ostream,idt):
	sw = StreamWriter(ostream,idt)
	module = e.container

	sw.writeln('class %s:'%e.getName() )
	sw.idt_inc()
	sw.writeln('# -- SEQUENCE --')
	sw.writeln('def __init__(self,array):')
	sw.idt_inc()
	sw.writeln('self.ds = array')
	sw.writeln('')

	sw.idt_dec()
	sw.writeln('def marshall(self):')
	sw.idt_inc()
	sw.writeln("d = '' ")
	sw.writeln("d += struct.pack('!I',len(self.ds))" )
	if isinstance( e.type,Builtin) and e.type.type=='byte':
		sw.writeln("d+=self.ds")
		sw.writeln("return d").wln()
	else:
		sw.writeln('for o in self.ds:')
		sw.idt_inc()
		if isinstance( e.type,Builtin):
			s = Builtin_Python.serial(e.type.type,'o',idt)
			sw.writeln( s)
		elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
			s = "container = %s(o)"%e.type.getTypeName(module)
			sw.writeln(s)
			s = "d += container.marshall()"
			sw.writeln(s)
		else:
			sw.writeln("d += o.marshall()")
		sw.idt_dec()
		sw.writeln('return d')
		sw.writeln('')

	#def unmarshall()

	sw.idt.dec()
	sw.writeln('def unmarshall(self,d,idx_=0):')
	sw.idt.inc()
	sw.writeln('idx = idx_')

	sw.writeln("try:")
	sw.idt_inc()
	sw.writeln("size_,= struct.unpack('!I',d[idx:idx+4])" )
	sw.writeln("idx += 4")
	if e.type.name == 'byte':
		sw.writeln('self.ds = d[idx:idx+size_]')
		sw.writeln('idx+=size_')
#		sw.writeln('return True,idx')
		sw.idt_dec()
	else:
		sw.writeln("p = 0")


		sw.writeln("while p < size_:")
		sw.idt_inc()

		if isinstance(e.type,Builtin):
			s= Builtin_Python.unserial(e.type.type,'v','d',sw.idt,'idx')
			sw.writeln(s)
			sw.writeln('self.ds.append(v)')
		elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):
			if isinstance( e.type,Sequence):
				sw.writeln("o =[]")
			else:
				sw.writeln("o ={}")
	#		if isinstance(e.type,Sequence) and e.type.type.name=='byte':
	#			s= Builtin_Python.unserial('string','o','d',sw.idt)
	#			sw.writeln(s)
	#		else:
			sw.writeln("container = %s(o)"%e.type.getTypeName(module))
			sw.writeln("r,idx = container.unmarshall(d,idx)")
			sw.writeln('if not r: return False,idx')

			if isinstance(e.type,Sequence) and e.type.type.name =='byte':

				sw.writeln('o = container.ds')
			sw.writeln("self.ds.append(o)")
		else:
			sw.writeln("o = %s()"%e.type.getTypeName(module))
			s = "r,idx = o.unmarshall(d,idx)"
			sw.writeln(s)
			sw.writeln('if not r: return False,idx')
			sw.writeln("self.ds.append(o)")

		sw.writeln("p+=1").idt_dec()

		sw.idt_dec()
	sw.writeln("except:")
	sw.idt_inc()
	sw.writeln("traceback.print_exc()")
	sw.writeln("return False,idx")
	sw.idt_dec()
	sw.writeln("return True,idx")



def createCodeDictionary(e,ostream,idt):
	sw = StreamWriter(ostream,idt)
	module = e.container
	sw.writeln('class %s:'%e.getName() )
	sw.idt_inc()
	sw.writeln('# -- THIS IS DICTIONARY! --')
	sw.writeln('def __init__(self,ds={}):')	#将hash数据{}传递进来
	sw.idt_inc()
	sw.writeln('self.ds = ds')
	sw.writeln('')

	sw.idt_dec()
	sw.writeln('def marshall(self):')
	sw.idt_inc()
	sw.writeln("d = '' ")
	sw.writeln("d += struct.pack('!I',len(self.ds.keys()))" )
	sw.writeln('for k,v in self.ds.items():')
	sw.idt_inc()
#	print '9999.',e.first.type,e.second.type
	if isinstance( e.first,Builtin):
		s = Builtin_Python.serial(e.first.type,'k',idt)
		sw.writeln( s)
	elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
		if isinstance( e.first,Sequence) and e.first.type.name=='byte':
			s = Builtin_Python.serial('string','k',idt)
			sw.writeln( s)
		else:
			s = "container = %s(k)"%e.first.getTypeName(module)
			sw.writeln(s)
			s = "d += container.marshall()"
			sw.writeln(s)
	else:
		sw.writeln("d += k.marshall()")

	if isinstance( e.second,Builtin):
		s = Builtin_Python.serial(e.second.type,'v',idt)
		sw.writeln( s)
	elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
		if isinstance(e.second,Sequence) and e.second.type.name=='byte':
			s = Builtin_Python.serial('string','v',idt)
			sw.writeln( s)
		else:
			s = "container = %s(v)"%e.second.getTypeName(module)
			sw.writeln(s)
			s = "d += container.marshall()"
			sw.writeln(s)
	else:
		sw.writeln("d += v.marshall()")

	sw.idt_dec()
	sw.writeln('return d')

	sw.writeln('')
	#def unmarshall()

	sw.idt.dec()
	sw.writeln('def unmarshall(self,d,idx_=0):')
	sw.idt.inc()
	sw.writeln('idx = idx_')

	sw.writeln("try:")
	sw.idt_inc()
	sw.writeln("_size,= struct.unpack('!I',d[idx:idx+4])" )
	sw.writeln("p = 0")
	sw.writeln("idx += 4") # hash pair的数量
	sw.writeln("while p < _size:")
	sw.idt_inc()
	if isinstance(e.first,Builtin):
		s= Builtin_Python.unserial(e.first.type,'x','d',sw.idt)
		sw.writeln(s)
	elif isinstance(e.first,Sequence) :# or initBuiltinTypes(e.first,Dictionary):
		s = "x=[]"
		sw.writeln(s)
		if e.first.type.name=='byte':
			s= Builtin_Python.unserial('string','x','d',sw.idt,'idx')
			sw.writeln(s)
		else:
			s = "container = %s(x)"%e.first.getTypeName(module)
			sw.writeln(s)
			sw.writeln( 'r,idx = container.unmarshall(d,idx)')
			sw.writeln('if not r: return False,idx')
	elif isinstance(e.first,Dictionary):
		sw.writeln("x={}")
		s = "container = %s(x)"%e.first.getTypeName(module)
		sw.writeln(s)
		sw.writeln( 'r,idx = container.unmarshall(d,idx)')
		sw.writeln('if not r: return False,idx')
	else:
		s = "x = %s()"%e.first.getTypeName(module)
		sw.writeln(s)
		s = "r,idx = x.unmarshall(d,idx)"
		sw.writeln(s)
		sw.writeln('if not r: return False,idx')

	# second.
	if isinstance(e.second,Builtin):
		s= Builtin_Python.unserial(e.second.type,'y','d',sw.idt)
		sw.writeln(s)
	elif isinstance(e.second,Sequence) :# or initBuiltinTypes(e.first,Dictionary):
		s = "y=[]"
		sw.writeln(s)
		if e.second.type.name == 'byte':
			s= Builtin_Python.unserial('string','y','d',sw.idt)
			sw.writeln(s)
		else:
			s = "container = %s(y)"%e.second.getTypeName(module)
			sw.writeln(s)
			sw.writeln( 'r,idx = container.unmarshall(d,idx)')
			sw.writeln('if not r: return False,idx')
	elif isinstance(e.second,Dictionary):
		sw.writeln("y={}")
		s = "container = %s(y)"%e.second.getTypeName(module)
		sw.writeln(s)
		sw.writeln( 'r,idx = container.unmarshall(d,idx)')
		sw.writeln('if not r: return False,idx')
	else:
		s = "y = %s()"%e.second.getTypeName(module)
		sw.writeln(s)
		s = "r,idx = y.unmarshall(d,idx)"
		sw.writeln(s)
		sw.writeln('if not r: return False,idx')

	sw.writeln("self.ds[x] = y")
	sw.writeln("p+=1")

	sw.idt_dec()
	sw.idt_dec()
	sw.writeln("except:")
	sw.idt_inc()
	sw.writeln("traceback.print_exc()")
	sw.writeln("return False,idx")
	sw.idt_dec()
	sw.writeln("return True,idx")


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



def createServant(e,sw):
	global  interface_defs,ifcnt
	module = e.container
	# CREATE SERVANT CLASS
	sw.writeln('class %s(tce.RpcServantBase):'%e.getName() )
	sw.idt_inc()
	sw.writeln("# -- INTERFACE -- ")

	#写入对应的delegate 类对象
	sw.writeln("def __init__(self):").idt_inc()
	sw.writeln('tce.RpcServantBase.__init__(self)')

	sw.writeln("if not hasattr(self,'delegatecls'):").idt_inc()
	sw.writeln("self.delegatecls = {}").idt_dec()
	sw.writeln("self.delegatecls[%s] = %s_delegate"%(e.ifidx,e.getName()) )

	sw.idt_dec().wln()
	for m in e.list: # function list
		params=[]
		for p in m.params:
			params.append( p.id )
		s = string.join( params,',')
		if s: s = ','+s
		sw.writeln('def %s(self%s,ctx):'%(m.name,s) ).idt_inc()
		#------------定义默认返回函数----------------------

		if isinstance( m.type ,Builtin ):
			if m.type.type =='void':
				sw.writeln("pass")
				sw.idt_dec().wln()
				continue
			# else:
			# 	sw.writeln("return %s"%m.type.getTypeDefaultValue(module))
		sw.writeln("return %s"%m.type.getTypeDefaultValue(module)).wln()
		# elif isinstance(m.type,Sequence):
		# 	sw.writeln("return [ ]")
		# elif isinstance(m.type,Dictionary):
		# 	sw.writeln("return {}")
		# else:
		# 	sw.writeln("return %s()"%m.type.name)
		sw.idt_dec()
	sw.idt_dec().idt_dec().wln()
	#----------------------------------

def createServantDelegate(e,ifidx,sw):
	global  interface_defs,ifcnt
	module = e.container
	#服务对象调用委托
	idt = sw.idt
	sw.writeln("class %s_delegate:"%e.getName()).idt_inc()
	sw.writeln("def __init__(self,inst,adapter,conn=None):").idt_inc()
	sw.writeln("self.index = %s"%ifidx)	#接口的索引编号
	sw.writeln("self.optlist={}")  #记录成员函数 索引对应的函数入口
	sw.writeln("self.id = '' ")  #唯一服务类
	sw.writeln("self.adapter = adapter")

	for opidx,m in enumerate(e.list): # function list
		sw.writeln("self.optlist[%s] = self.%s"%(opidx,m.name)) #直接保存 twoway 和 oneway 函数入口
	sw.wln()

	sw.writeln("self.inst = inst")

	sw.idt_dec().writeln('')
	for opidx,m in enumerate(e.list): # function list
		sw.writeln('def %s(self,ctx):'%(m.name) ).idt_inc()
		sw.writeln('tce.log_debug("callin (%s)")'%m.name)
		params=[]
		sw.writeln("d = ctx.msg.paramstream ")
		sw.writeln("idx = 0")
		#防止参数重命名，加上 _p_前缀
		for p in m.params:
			if isinstance(p.type,Builtin):
				s = Builtin_Python.unserial(p.type.type,'_p_'+p.id,'d',idt)
				sw.writeln(s)

			elif isinstance(p.type,Sequence) :
				sw.writeln("_p_%s =[] "%p.id)
				if p.type.type.name == 'byte':
					s = Builtin_Python.unserial('string','_p_'+p.id,'d',idt)
					sw.writeln(s)
				else:
					sw.writeln('container = %s(_p_%s)'%(p.type.getTypeName(module),p.id))
					sw.writeln('r,idx = container.unmarshall(d,idx)')
					sw.writeln("if not r: return False") #发起流消息到接口参数的转换失败
			elif isinstance(p.type,Dictionary):
				sw.writeln("_p_%s ={} "%p.id)
				sw.writeln('container = %s(_p_%s)'%(p.type.getTypeName(module),p.id))
				sw.writeln('r,idx = container.unmarshall(d,idx)')
				sw.writeln("if not r: return False") #发起流消息到接口参数的转换失败
			else:
				sw.writeln('_p_%s = %s()'%(p.id,p.type.getTypeName(module)))
				sw.writeln('r,idx = _p_%s.unmarshall(d,idx)'% p.id )
				sw.writeln('if not r: return False')
			params.append(p.id)
		params = map( lambda x: '_p_'+x,params)
		ps = string.join(params,',')

		if ps: ps = ps + ','

		sw.writeln("cr = None")

		if m.type.name =='void':
			sw.writeln("self.inst.%s(%sctx)"%(m.name,ps) )
			# sw.writeln("return True").idt_dec().wln()
			sw.writeln("if ctx.msg.calltype & tce.RpcMessage.ONEWAY: return True")

			# continue
		else:
			sw.writeln("cr = self.inst.%s(%sctx)"%(m.name,ps) )
			sw.writeln("if not cr : return True")

		#		if isinstance(m.type,Builtin) and m.type.type =='void':
		#			sw.writeln("self.inst.%s(%sctx)"%(m.name,ps) )
		#		else:
		#			sw.writeln("cr = self.inst.%s(%sctx)"%(m.name,ps) )
		#			sw.writeln("if cr == None:").idt_inc()
		#			if isinstance(m.type,Sequence):
		#				sw.writeln("cr = []")
		#				sw.idt_dec()
		#			elif isinstance(m.type,Dictionary):
		#				sw.writeln("cr = {}")
		#				sw.idt_dec()
		#			else:
		#				sw.writeln("pass").idt_dec()


		#		sw.writeln("if ctx.msg.calltype & tce.RpcMessage.CALL_ONE_WAY:").idt_inc()
		#		sw.writeln("return False").idt_dec()
		#		sw.wln()

		sw.writeln("d = '' ")
		sw.writeln("m = tce.RpcMessageReturn(self.inst)")
		sw.writeln("m.sequence = ctx.msg.sequence") #返回事务号与请求事务号必须一致
		sw.writeln('m.callmsg = ctx.msg')
		sw.writeln('m.ifidx = ctx.msg.ifidx')
		sw.writeln('m.call_id = ctx.msg.call_id')
		sw.writeln('m.conn = ctx.msg.conn')
		sw.writeln('m.extra = ctx.msg.extra')

		# sw.writeln("if self.inst.msg_post_expired_time:").idt_inc()
		# sw.writeln("m.extra.setPropertyValue(tce.RpcMessageDeliveryMgr.POST_EXPIRE_TIME,self.inst.msg_post_expired_time) ").idt_dec()

		if isinstance( m.type ,Builtin ):
			s = Builtin_Python.serial(m.type.type,'cr',idt,'d')
			if s:	sw.writeln(s)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			if isinstance(m.type,Sequence) and m.type.type.name=='byte':
				s = Builtin_Python.serial('string','cr',idt,'d')
				if s:	sw.writeln(s)
			else:
				sw.writeln('container = %s(cr)'%(m.type.getTypeName(module)) )
				sw.writeln('d += container.marshall()' )
		else:
			sw.writeln("d += cr.marshall()")

#		sw.writeln("if d: m.addParam(d)")
		sw.writeln('if d: m.paramstream += d')
		sw.writeln("ctx.conn.sendMessage(m)")
		sw.writeln("return True").idt_dec().wln()

fileifx = open('ifxdef.txt','w') #接口表文件

def createCodeInterface(e,ostream,idt,idx):
	module = e.container
	global  interface_defs,ifcnt
	ifidx = ifcnt
	ifcnt+=1

	#-------- index of if-cls from extern setting in file
	import tce_util
	ifname = "%s.%s"%(module.name,e.name)
	r = tce_util.getInterfaceIndexWithName(ifname)
	# print 'get if-index:%s with-name:%s'%(r,ifname)
	if r != -1:
		ifidx = r
	#--- end

	sw = StreamWriter(ostream,idt)
	e.ifidx = ifidx

	interface_defs[ifidx] = {'e':e,'f':{}}

	fileifx.write('<if id="%s" name="%s.%s"/>\n'%(ifidx,module.name,e.name))
	fileifx.flush()

	createServant(e,sw)
	createServantDelegate(e,ifidx,sw)

	sw.writeln('')


	#------------Create Proxy -------------
	# 创建代理
	# prx.conn -- 指向网络连接对象 RpcConnection
	# prx.delta -- 可用于上下文数据传递
	#void函数类型不支持异步调用

	sw.idt_dec()
	sw.writeln('class %sPrx(tce.RpcProxyBase):'%e.getName() ).idt_inc()
	sw.writeln("# -- INTERFACE PROXY -- ")
	sw.writeln("def __init__(self,conn):").idt_inc()
	sw.writeln('tce.RpcProxyBase.__init__(self)')
	sw.writeln("self.conn = conn")
	sw.writeln("self.delta = None")
	sw.writeln("pass").idt_dec().wln()

	# Create()
	sw.writeln("@staticmethod")
	sw.writeln("def create(ep,af= tce.AF_WRITE | tce.AF_READ):").idt_inc()
	sw.writeln("ep.open(af)")
	sw.writeln("conn = ep.impl")
	sw.writeln("proxy = %sPrx(conn)"%(e.getName() ))
	sw.writeln("return proxy").idt_dec()
	sw.wln()

	sw.writeln("@staticmethod")
	sw.writeln("def createWithEpName(name):").idt_inc()
	sw.writeln('ep = tce.RpcCommunicator.instance().currentServer().findEndPointByName(name)')
	sw.writeln('if not ep: return None')
	sw.writeln('conn = ep.impl')
	sw.writeln("proxy = %sPrx(conn)"%(e.getName() ))
	sw.writeln("return proxy").idt_dec()
	sw.wln()

	sw.writeln("@staticmethod")
	sw.writeln("def createWithProxy(prx):").idt_inc()
	sw.writeln("proxy = %sPrx(prx.conn)"%(e.getName() ))
	sw.writeln("return proxy").idt_dec()
	sw.wln()

	#-- end Create()

	for opidx,m in enumerate(e.list): # function list
		params=[]

		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象


		for p in m.params:
			params.append( p.id )
		s = string.join( params,',')
		# 函数定义开始
		if s: s = ','+s

		sw.writeln('#extra must be map<string,string>')
		sw.writeln('def %s(self%s,timeout=None,extra={}):'%(m.name,s) ).idt_inc()
		sw.writeln("# function index: %s"%idx).wln()
		sw.resetVariant()
		# sw.writeln("ecode = tce.RpcConsts.RPCERROR_SUCC")
		v1 = sw.newVariant('m')
		mm = v1
		sw.writeln("%s = tce.RpcMessageCall(self)"%v1)
		sw.writeln("%s.ifidx = %s"%(v1,ifidx))
		sw.writeln("%s.opidx = %s"%(v1,opidx))
		sw.writeln('%s.extra.setStrDict(extra)'%v1)
		# sw.writeln("if self.msg_post_expired_time:").idt_inc()
		# sw.writeln("%s.extra.setPropertyValue(tce.RpcMessageDeliveryMgr.POST_EXPIRE_TIME,self.msg_post_expired_time) "%(v1,)).idt_dec()

		d1 = sw.newVariant('d')
		c1 = sw.newVariant('container')
		for p in m.params:

			sw.writeln("%s = '' "%d1)
			if isinstance(p.type,Builtin):
				s = Builtin_Python.serial(p.type.type,p.id,idt,d1)
				sw.writeln(s)
			elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
				if isinstance(p.type,Sequence) and p.type.name=='byte':
					s = Builtin_Python.serial('string',p.id,idt,d1)
					sw.writeln(s)
				else:

					sw.writeln('%s = %s(%s)'%(c1,p.type.getTypeName(module),p.id))
					sw.writeln('%s += %s.marshall()'%(d1,c1))
			else:
				sw.writeln("%s += %s.marshall()"%(d1,p.id) )
#			sw.writeln("m.addParam(d)")
			sw.writeln('%s.paramstream += %s'%(v1,d1))
		sw.writeln("%s.prx = self"%v1)
		sw.writeln('%s.conn = %s.prx.conn'%(v1,v1))
		sw.writeln('%s.call_id = tce.RpcCommunicator.instance().currentServer().getId()'%v1)
		r1 = sw.newVariant('r')
		sw.writeln("%s = self.conn.sendMessage(%s)"%(r1,v1))
		sw.writeln("if not %s:"%r1).idt_inc()
		sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)")
		sw.idt_dec()

		#同步调用, 超时等待产生异常
		sw.writeln("if not timeout: timeout = tce.RpcCommunicator.instance().getRpcCallTimeout()")
		v2 = sw.newVariant('m')
		sw.writeln("%s = None"%v2)
		sw.writeln("try:").idt_inc()
		sw.writeln("%s = %s.mtx.get(timeout=timeout)"%(v2,v1)).idt_dec() #永远等待，直到链接断开通知取消等待
		sw.writeln("except:").idt_inc()
		sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_TIMEOUT)").idt_dec()


		#如果发送消息 被设置了错误代码，即刻抛出异常，
		# 错误可能：远端执行错误、连接断开
		sw.writeln("if %s.errcode != tce.RpcConsts.RPCERROR_SUCC:"%v2).idt_inc()
		sw.writeln("raise tce.RpcException(%s.errcode)"%v2).idt_dec()


		sw.writeln("%s = %s"%(v1,v2))

		if m.type.name != 'void':
			#sw.writeln("return ").idt_dec()
			#分解返回值
			idx = sw.newVariant('idx')
			p = sw.newVariant('p')
			r = sw.newVariant('r')
			d = sw.newVariant('d')
			container = sw.newVariant('container')

			sw.writeln("%s = 0"%idx)
			sw.writeln("%s = %s.paramstream"%(d,v1))
			sw.writeln("%s = None"%p)
			sw.writeln("%s = False"%r)
			sw.writeln("try:").idt_inc()
			if isinstance(m.type,Builtin):
				sw.writeln("%s = None"%p)
				s = Builtin_Python.unserial(m.type.type,p,d,idt,idx)
				sw.writeln(s)
			elif isinstance(m.type,Sequence):
				if m.type.type.name=='byte': #加速读取sequece字节数组
					s = Builtin_Python.unserial('string',p,d,idt,idx)
					sw.writeln(s)
				else:
					sw.writeln("%s =[]"%p)
					sw.writeln('%s = %s(%s)'%(container,m.type.getTypeName(module),p))
					sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,container,d,idx))
			elif isinstance(m.type,Dictionary):
				sw.writeln("%s ={}"%p)
				sw.writeln('%s = %s(%s)'%(container,m.type.getTypeName(module),p))
				sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,container,d,idx))
			else:
				sw.writeln('%s = %s()'%(p,m.type.getTypeName(module)))
				sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,p,d,idx))

			sw.idt_dec()
			sw.writeln("except:").idt_inc()
			sw.writeln("traceback.print_exc()")
			sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_UNSERIALIZE_FAILED)")
			sw.idt_dec()

			sw.writeln("return %s"%p)
		#end --
		sw.idt_dec().wln()
		#--------------------------------------------------

		#-----  async call -------------------------------
		params=[]
		# if m.type.name !='void': #异步调用接口必须有返回值
		if True:
			sw.resetVariant()

			for p in m.params:
				params.append( p.id )
			s = string.join( params,',')
			# 函数定义开始
			if s: s = ','+s
			sw.writeln('def %s_async(self%s,async,cookie=None,extra={}):'%(m.name,s) ).idt_inc()
			sw.writeln("# function index: %s"%idx).wln()

			mm = sw.newVariant('m')
			ecode = sw.newVariant('ecode')
			d = sw.newVariant('d')
			container = sw.newVariant('container')
			r = sw.newVariant('r')

			sw.writeln("%s = tce.RpcConsts.RPCERROR_SUCC"%ecode)
			sw.writeln("%s = tce.RpcMessageCall(self)"%mm)
			sw.writeln('%s.cookie = cookie'%mm) # 2015-7-14 scott
			sw.writeln("%s.ifidx = %s"%(mm,ifidx) )
			sw.writeln("%s.opidx = %s"%(mm,opidx) )
			sw.writeln('%s.extra.setStrDict(extra)'%mm)

			for p in m.params:
				sw.writeln("%s = '' "%d)
				if isinstance(p.type,Builtin):
					s = Builtin_Python.serial(p.type.type,p.id,idt,d)
					sw.writeln(s)
				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name=='byte':
						s = Builtin_Python.serial('string',p.id,idt,d)
						sw.writeln(s)
					else:
						sw.writeln('%s = %s(%s)'%(container,p.type.getTypeName(module),p.id))
						sw.writeln('%s += %s.marshall()'%(d,container))
				else:
					sw.writeln("%s += %s.marshall()"%(d,p.id) )
				sw.writeln('%s.paramstream += %s'%(mm,d))
			sw.writeln("%s.prx = self"%(mm))
			sw.writeln('%s.conn = %s.prx.conn'%(mm,mm))
			sw.writeln('%s.call_id = tce.RpcCommunicator.instance().currentServer().getId()'%mm)

			sw.writeln("%s.async = async"%mm)
			sw.writeln("%s.asyncparser = %sPrx.%s_asyncparser"%(mm,e.getName(),m.name ) )
			sw.writeln("%s = self.conn.sendMessage(%s)"%(r,mm))
			sw.writeln("if not %s:"%r).idt_inc()
			sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)")
			sw.idt_dec()
			#end --
			sw.idt_dec().wln() #back to def

		#----- end async call ------------------------------
		# -- 生成 异步调用 函数返回值 解析的函数 ，静态函数
		# 异步调用返回, void 类型不能异步返回
		# if m.type.name !='void':
		if True:    #支持void返回类型的异步调用 async  2013.9.19
			sw.resetVariant()

			sw.writeln("@staticmethod")
			# m - 消息发起者 ; m2 - 远端返回消息
			sw.writeln('def %s_asyncparser(m,m2):'%(m.name,) ).idt_inc()
			sw.writeln("# function index: %s , m2 - callreturn msg."%idx).wln() #stream,user,prx)

			stream = sw.newVariant('stream')
			user = sw.newVariant('user')
			prx = sw.newVariant('prx')
			idx = sw.newVariant('idx')
			d = sw.newVariant('d')
			r = sw.newVariant('r')
			p = sw.newVariant('p')
			container = sw.newVariant('container')

			sw.writeln("%s = m2.paramstream"%stream)
			sw.writeln("%s = m.async"%user) # 用户异步接收函数
			sw.writeln("%s = m.prx"%prx)
			#出现异常，不进行提示，！！ 也许应该讲错误信息传递给异步接收函数
			sw.writeln("if m2.errcode != tce.RpcConsts.RPCERROR_SUCC: return ") #skipped error


			sw.writeln("try:").idt_inc()
			sw.writeln("%s = 0"%idx)
			sw.writeln("%s = %s"%(d,stream))
			sw.writeln("%s = True"%r)
			if isinstance(m.type,Builtin):
				if m.type.name!='void':
					sw.writeln("%s = None"%p)
					s = Builtin_Python.unserial(m.type.type,p,d,idt,idx)
					sw.writeln(s)
			elif isinstance(m.type,Sequence):
				if m.type.type.name=='byte':
					s = Builtin_Python.unserial('string',p,d,idt,idx)
					sw.writeln(s)
				else:
					sw.writeln("%s =[]"%p)
					sw.writeln('%s = %s(%s)'%(container,m.type.getTypeName(module),p))
					sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,container,d,idx))
			elif isinstance(m.type,Dictionary):
				sw.writeln("%s ={}"%p)
				sw.writeln('%s = %s(%s)'%(container,m.type.getTypeName(module),p))
				sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,container,d,idx))
			else:
				sw.writeln('%s = %s()'%(p,m.type.getTypeName(module)))
				sw.writeln('%s,%s = %s.unmarshall(%s,%s)'%(r,idx,p,d,idx))
			sw.writeln("if %s:"%r).idt_inc()
			#反射到用户代码
			if m.type.name!='void':
				sw.writeln("%s(%s,%s,m.cookie)"%(user,p,prx)).idt_dec().idt_dec()
			else:
				sw.writeln("%s(%s,m.cookie)"%(user,prx)).idt_dec().idt_dec()

			sw.writeln("except:").idt_inc()
			sw.writeln("traceback.print_exc()")
			sw.idt_dec().wln()
			sw.idt_dec().wln()
		# ---  END  async callback --

		#--------BEGIN ONEWAY CALL ----------------
		#-- 创建oneway的调用方法 (无需处理返回等待)
		# 仅仅 void类型支持单向调用

		if m.type.name =='void':
			sw.resetVariant()
			params =[]
			for p in m.params:
				params.append( p.id )
			s = string.join( params,',')
			if s: s = ','+s
			sw.writeln('def %s_oneway(self%s,extra={}):'%(m.name,s) ).idt_inc()
			sw.writeln("# function index: %s"%idx).wln()

			mm = sw.newVariant('m')
			d = sw.newVariant('d')
			container = sw.newVariant('container')
			r = sw.newVariant('r')


			sw.writeln("try:").idt_inc()
			sw.writeln("%s = tce.RpcMessageCall(self)"%mm)
			sw.writeln("%s.ifidx = %s"%(mm,ifidx) )
			sw.writeln("%s.opidx = %s"%(mm,opidx))
			sw.writeln("%s.calltype |= tce.RpcMessage.ONEWAY"%mm)
			sw.writeln('%s.prx = self'%mm)
			sw.writeln('%s.conn = %s.prx.conn'%(mm,mm))
			sw.writeln('%s.call_id = tce.RpcCommunicator.instance().currentServer().getId()'%mm)
			sw.writeln('%s.extra.setStrDict(extra)'%mm)

			for p in m.params:
				sw.writeln("%s = '' "%d)
				if isinstance(p.type,Builtin):
					s = Builtin_Python.serial(p.type.type,p.id,idt,d)
					sw.writeln(s)

				elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
					if isinstance(p.type,Sequence) and p.type.type.name=='byte':
						s = Builtin_Python.serial('string',p.id,idt,d)
						sw.writeln(s)
					else:
						sw.writeln('%s = %s(%s)'%(container,p.type.getTypeName(module),p.id))
						sw.writeln('%s += %s.marshall()'%(d,container))
				else:
					sw.writeln("%s += %s.marshall()"%(d,p.id) )
				sw.writeln('%s.paramstream += %s'%(mm,d))

			sw.writeln("%s = self.conn.sendMessage(%s)"%(r,mm))
			sw.writeln("if not %s:"%r).idt_inc()
			sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)").idt_dec()


			sw.idt_dec()
			sw.writeln("except:").idt_inc()
			sw.writeln("traceback.print_exc()")
			sw.writeln("raise tce.RpcException(tce.RpcConsts.RPCERROR_SENDFAILED)")
			sw.idt_dec()
			sw.idt_dec().wln()
		#-- end onway --------------


	return



def createCodeFrame(module,e,idx,ostream ):
	idt = Indent()

	if isinstance(e,Interface):
		# print 'interface:',e.name
		createCodeInterface(e,ostream,idt,idx)

	if isinstance(e,Sequence):
		createCodeSequence(e,ostream,idt)
		pass

	if isinstance(e,Dictionary):
		createCodeDictionary(e,ostream,idt)

	if isinstance(e,Struct):
		createCodeStruct(module,e,ostream,idt)
		return

	# createCodeInterfaceMapping() #创建 链接上接收的Rpc消息 根据其ifx编号分派到对应的接口和函数上去

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
import tcelib as tce

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



def createCodes():
	#file = sys.argv[1]
	global  interface_defs,ifcnt
	# global curr_idl_path

	file = 'idl/main.idl'

	idlfiles = ''

	ostream = Outputer()
	# ostream.addHandler(sys.stdout)
	outdir = './'
	argv = sys.argv
	while argv:
		p = argv.pop(0)
		if p =='-o':    #输出目录
			p = argv.pop(0)
			outdir = p
			#f = open(p,'w')
			#ostream.addHandler(f)
		if p =='-i':
			if argv:
				p = argv.pop(0)
				file = p
		if p =='-if': # 接口起始下标，如多个module文件并存，则同坐此参数区分开
			if argv:
				ifcnt = int(argv.pop(0))


	if not os.path.exists(outdir):
		os.mkdir(outdir)

	idlfiles = file.strip().split(',')

	#读入idl定义内容
	# fp = None
	# content = None

	for file in idlfiles:
		# try:
		# 	fp = open(file,'r')
		# 	content = fp.read()
		# 	fp.close()
		# except:
		# 	print 'access file: %s failed!'%file
		# 	sys.exit()
		# if content.find('\n\r') ==-1:
		# 	content.replace('\r','\n\r')

		print file
		idl_file = file
		lexparser.curr_idl_path = os.path.dirname(idl_file)


		parse_idlfile(idl_file)

	unit = syntax_result()

	# print global_modules_defs

	# for name, module in global_modules_defs.items():
	#--依次遍历每个module
	for module in global_modules:
		name = module.name
		# print 'module:',name,module.ref_modules.keys()
		# print module.children
		f = open(os.path.join(outdir,name+'.py'),'w')
		ostream.clearHandler()
		ostream.addHandler(f)
		ostream.write(headtitles)
		sw = StreamWriter(ostream,Indent())
		for ref in module.ref_modules.keys():
			sw.writeln('import %s'%ref)

		for idx,e in enumerate(module.list):
			createCodeFrame(module,e,idx,ostream)
			ostream.write(NEWLINE)



lexparser.lang_kws = ['def', 'import', 'from', 'type', 'str', 'int', 'float', 'class']
# lexparser.lang_kws = ['def','import','from','int','float','class']



def usage():
	howto='''
	python tce2py.py -i a.idl,b.idl,.. -o ./
	'''
if __name__ =='__main__':
	createCodes()


