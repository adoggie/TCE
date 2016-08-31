#--coding:utf-8--

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
# 终于到了拿cpp开刀了，哇哈哈
# stl reference: http://msdn.microsoft.com/zh-tw/library/windows/apps/xaml/9h24a8cd

# 注意: 
# 1. void型函数不支持异步调用  ； 
# 2. dictionary类型的key必须为 primitive数据类型，不能为struct、sequence、dictionary做key，除非自动生成 < 的比较函数
# 3. 一个adpater上对应 host+port，且多个module的servant不能加在同一个adaper内（自动生成索引编号引起重复）
# 后续可以支持 外部输入idx索引起始值来保证不同module的servant在adapter中并存

#2012.12.31
# 1. 增加输出制定接口的idlmaping 代码，防止过多的代码生成
#    增加过滤文件来制定生成的接口

import os
import os.path
import string

import lexparser
from lexparser import *
from mylex import syntax_result




interface_idx = [ ]

idx_datatype=1
idx_interface = 1


dataMapStream =0



class Buffer:
	def __init__(self):
		self.d = ''

	def write(self,s):
		self.d+=s

	def close(self):
		self.d=''


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

	def struct_end(self):
		self.idt_dec().newline().brace2()
		self.ostream.write(';')
		return self.wln()

	def define_var(self,name,type,val=None):
		txt ="%s %s"%(type,name)
		if val:
			txt+=" = "+ val
		txt+=";"
		self.writeln(txt)

	def createPackage(self,name,path):
		if path and  not  os.path.exists(path):
			os.mkdir(path)
		if path:
			name = path +'/' + name
		self.ostream = open(name+'.h','w')

		pass

	#进入包空间
	def pkg_enter(self,name):
		self.packages.append(name)
		self.writeln('#ifndef _%s_H'%name)
		self.writeln('#define _%s_H'%name)
		self.writeIncludes()
		self.write("namespace %s "%name).brace1().wln().idt_inc()
		#os.chdir(name)

	def pkg_current(self):
		import string
		return string.join(self.packages,'::')

	def pkg_leave(self):
		pkg = self.packages[-1]
		self.idt_dec().brace2()
		self.wln()
		self.writeln('#endif')
		self.ostream.close()
		#os.chdir('../')

#	def pkg_begin(self):
#		pkg = self.packages[-1]
#		if not pkg:return
#		self.writeIncludes()
#		self.write("namesapce %s "%pkg).brace1().wln().idt_dec()
#
#	def pkg_end(self):
#		self.idt_dec().wln().brace2()
#		self.ostream.close()

	def classfile_enter(self,name,file=''):
		pass
#		if file:
#			self.ostream = open(file+'.as','w')
#		else:
#			self.ostream = open(name+'.as','w')
		#self.pkg_begin()
		#self.writeIncludes()
#		self.idt_inc()

	def classfile_leave(self):
		pass
#		self.idt_dec()
#		self.pkg_end()
#		self.ostream.close()


gbufwriter = StreamWriter(ostream=Buffer())


class Builtin_Python:
	def __init__(self):
		pass

	@staticmethod
	def serial(typ,val,idt,sw=None,stream=None):
		# typ - builtin ; val - variant name
		s=''
		if not stream:
			stream = 'd'
		if typ == 'byte':
			sw.writeln("%s.writeByte(%s);"%(stream,val))
		elif typ == 'bool':
			sw.writeln("if(%s == true){"%val).idt_inc()
			sw.writeln("%s.writeByte(1);"%(stream)).idt_dec()
			sw.writeln("}else{").idt_inc()
			sw.writeln("%s.writeByte(0);"%(stream))
#			idt_dec().brace2().wln()
			sw.idt_dec().newline().brace2().wln()


		elif typ == 'short':
			sw.writeln("%s.writeShort(%s);"%(stream,val) )
		elif typ == 'int':
			sw.writeln("%s.writeInt(%s);"%(stream,val))
		elif typ == 'long': #,'double'):
			sw.writeln("%s.writeInt64(%s);"%(stream,val) )
		elif typ =='double':
			sw.writeln("%s.writeDouble(%s);"%(stream,val) )
		elif typ == 'float': #,'double'):
			sw.writeln("%s.writeFloat(%s);"%(stream,val) )
		elif typ =='string':
			# 添加4字节头 长度
#			sw.writeln("%s.writeInt(%s.size());"%(stream,val))
			sw.writeln("%s.writeString(%s);"%(stream,val) )

		return s

	@staticmethod
	def unserial(typ,val,stream,idt,sw):
		s=''
		if typ == 'byte':
#			s = "%s, = struct.unpack('B',%s[idx:idx+1])"%(val,stream)
#			s+= NEWLINE + idt.str() + "idx+=1"
			sw.writeln("%s = %s.readByte();"%(val,stream))
		elif typ == 'bool':
			sw.newline().brace1().wln().idt_inc()
			sw.writeln("unsigned char _d = 0;")
			sw.writeln("_d = %s.readByte();"%(stream))
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
			sw.writeln("%s = %s.readInt64();"%(val,stream))
		elif typ == 'float':
			sw.writeln("%s = %s.readFloat();"%(val,stream))
		elif typ == 'double':
			sw.writeln("%s = %s.readDouble();"%(val,stream))
		elif typ =='string':
#			sw.newline().brace1().wln().idt_inc()
#			sw.writeln("unsigned int _d = 0;")
#			sw.writeln("_d = %s.readUnsignedInt();"%(stream))
			sw.writeln("%s = %s.readString();"%(val,stream)) #.idt_dec()
#			sw.newline().brace2().wln()

		return s


def createCodeStruct(e,sw,idt):

	sw.wln()
	params=[ ]
	for m in e.list:
#		v = m.type.getTypeDefaultValue()
		v = m.type.getMappingTypeName(e.container)
		params.append( (m.name,v) )
	pp =map(lambda x: '%s:%s'%(x[0],x[1]),params)
	ps = string.join(pp,',') #构造函数默认参数列表

	l ='struct %s{'%e.getName()
	sw.writeln(l)
	sw.writeln("// -- STRUCT -- ")
	sw.idt_inc()

	for m in e.list:
		d = m.type.getTypeDefaultValue(e.container)
		v = m.type.getMappingTypeName(e.container)
		sw.writeln("%s \t%s;"%(v,m.name))

	sw.writeln("//构造函数")
	sw.writeln('%s(){'%(e.getName(),) ).idt_inc()
	for m in e.list:
		d = m.type.getTypeDefaultValue(e.container)
		v = m.type.getMappingTypeName(e.container)
		sw.writeln("this->%s = %s;"%(m.name,d))
	sw.scope_end()

	sw.wln()
	sw.writeln('void marshall(tce::ByteArray& d){')
	sw.idt_inc()

	for m in e.list:
#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			s = Builtin_Python.serial(m.type.type,'this->' + m.name,idt,sw)
			#sw.writeln(s)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			sw.writeln('%shlp _c(this->%s);'%(m.type.name,m.name) )
			sw.writeln('_c.marshall(d);' )
			sw.scope_end()
		else:
			sw.scope_begin()
			sw.writeln("this->%s.marshall(d);"% m.name )
			sw.scope_end()
	sw.scope_end()

	sw.wln()

	#unmarshall()
	sw.writeln(u"//反序列化 unmarshall()".encode('utf-8'))
	sw.writeln("bool unmarshall(tce::ByteArray& d){" )

	sw.idt_inc()
	sw.writeln( "try{")
	sw.idt_inc()
	sw.writeln("bool r = false;")
	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type.type,'this->' + m.name,'d' , idt,sw)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			sw.writeln('%shlp _c(this->%s);'%(m.type.name,m.name) )
#			sw.define_var('_c',"%shlp"%m.type.name,"new %shlp(this.%s)"%(m.type.name,m.name) )
			sw.writeln("r = _c.unmarshall(d);")
			sw.writeln("if(!r){return false;}")
			sw.scope_end()
		else:
			sw.writeln('r = this->%s.unmarshall(d);'%m.name )
			sw.writeln("if(!r){return false;}")
			
	sw.writeln('r = true;')
	sw.idt_dec()
	sw.writeln('}catch(const tce::RpcException& e){' )
	sw.idt_inc()
	sw.writeln('return false;' )
	sw.idt_dec()
	sw.writeln("}")
	
	sw.writeln('return true;')
	sw.scope_end().writeln(' // --  end function -- ')	# end function
	sw.wln()

	sw.struct_end() # end class


def createCodeSequence(e,sw,idt):
	sw.wln()
#	sw.writeln('import %s;'%e.type.name)
	sw.writeln('struct %shlp{'%e.getName() )
	sw.idt_inc()
	sw.wln()
#	sw.writeln("typedef boost::shared_ptr< <std::vector<%s> > sequence_type_t;"%e.type.name)

	sw.writeln("typedef std::vector< %s >  sequence_type;"%e.type.getMappingTypeName(e.container))
#	sw.writeln("typedef const boost::shared_ptr< <std::vector<%s> > const_sequence_type;"%e.type.name)
	sw.writeln('//# -- SEQUENCE --')
	sw.writeln("sequence_type &ds;")
	sw.wln()
	sw.writeln('%shlp(sequence_type& ds_):ds(ds_){'%e.getName() ).idt_inc()
#	sw.writeln('this.ds = ds;')
	sw.scope_end().wln()

	sw.writeln('void marshall(tce::ByteArray& d){').idt_inc()
	sw.writeln("d.writeUnsignedInt((unsigned int)this->ds.size());")

	sw.writeln('for(size_t n=0; n< this->ds.size();n++){').idt_inc()

	if isinstance( e.type,Builtin):
		Builtin_Python.serial(e.type.type,'this->ds[n]',idt,sw)
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		sw.scope_begin()
#		sw.define_var('_c','%shlp'%e.type.name,'new %shlp(this.ds[n])'%(e.type.name) )
		sw.writeln('%shlp _c(this->ds[n]);'%e.type.name)
		sw.writeln('_c.marshall(d);')
		sw.scope_end()
	else:
		sw.writeln("this->ds[n].marshall(d);")

	sw.scope_end()
	sw.scope_end()
	sw.wln()
	#def unmarshall()

	sw.writeln('bool unmarshall(tce::ByteArray& d){').idt_inc()
	sw.writeln("bool r = false;")
	sw.writeln("try{").idt_inc()
	sw.define_var("_size","size_t","0")
	sw.writeln("_size = d.readUnsignedInt();")
	sw.writeln("for(size_t _p=0;_p < _size;_p++){").idt_inc()


	if isinstance(e.type,Builtin):
		sw.scope_begin()
		sw.define_var("_o",e.type.getMappingTypeName(e.container),e.type.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.type.type,'_o','d',sw.idt,sw)
		sw.writeln("this->ds.push_back(_o);")
		sw.scope_end()
	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):
		sw.scope_begin()
		if isinstance( e.type,Sequence):
			#sw.define_var("_o","Array","new Array()")
			sw.writeln('%shlp::sequence_type _o;'%e.type.name)

		else:
			#sw.define_var("_o","HashMap","new HashMap()")
			sw.writeln('%shlp::hash_type _o;'%e.type.name)

		sw.define_var('container(_o)','%shlp'%e.type.name)

#		sw.define_var("container","%shlp"%e.type.name,"new %shlp(_o)"%e.type.name)
		sw.writeln("r = container.unmarshall(d);")
		sw.writeln("if(!r) return false;")
		sw.writeln("this->ds.push_back(_o);")
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var("_o",e.type.name)
		sw.writeln("r= _o.unmarshall(d);")
		sw.writeln("if(!r) return false;")
		sw.writeln("this->ds.push_back(_o);")
		sw.scope_end()

	sw.scope_end() # end for{}
	sw.writeln('r = true;')
	sw.idt_dec()
	sw.writeln("}catch(const tce::RpcException& e){").idt_inc()
	sw.writeln("return false;")
	sw.scope_end()
	
	sw.writeln("return true;")
	sw.scope_end()

	sw.wln()
	sw.struct_end()
	sw.wln()



def createCodeDictionary(e,sw,idt):

	sw.wln()
	sw.writeln('struct %shlp {'%e.getName() ).idt_inc()
	sw.writeln('//# -- THIS IS DICTIONARY! --')
	sw.writeln('typedef std::map< %s,%s > hash_type;'%(e.first.getMappingTypeName(e.container),e.second.getMappingTypeName(e.container)))
	sw.writeln('typedef std::pair< %s,%s > hash_pair;'%(e.first.getMappingTypeName(e.container),e.second.getMappingTypeName(e.container)))
	sw.define_var('ds','hash_type&')
	sw.wln()
# sw.writeln('ds :HashMap = null;').wln()
	sw.writeln('%shlp(hash_type & ds_):ds(ds_){'%e.getName() ).idt_inc()	#将hash数据{}传递进来
#	sw.writeln('this.ds = ds;')
	sw.scope_end()
	sw.wln()

	sw.writeln('void marshall(tce::ByteArray& d){').idt_inc()
#	sw.writeln("d += struct.pack('!I',len(this.ds.keys()))" )

	sw.define_var('_size','size_t','0')
	sw.writeln("_size = this->ds.size();")
	sw.writeln('d.writeUnsignedInt( this->ds.size() );')
	sw.define_var('_itr','hash_type::iterator')
	sw.writeln('for(_itr=this->ds.begin();_itr!=this->ds.end();_itr++){').idt_inc()
	#sw.define_var('_pair','hash_pair&','*_itr')

	if isinstance( e.first,Builtin):
		sw.scope_begin()
		sw.define_var('k',e.first.getMappingTypeName(e.container),'_itr->first')
		Builtin_Python.serial(e.first.type,'k',idt,sw)
		sw.scope_end()
	elif isinstance( e.first,Sequence) or isinstance(e.first,Dictionary):
		sw.scope_begin()
		if isinstance(e.first,Sequence):
#			sw.define_var('container','%shlp::sequence_type'%e.first.name,'new %shlp(_pair.key as Array)'%(e.first.name) )
			sw.writeln('%shlp _c( *(%s *) &(_itr->first) );'%(e.first.name,e.first.getMappingTypeName(e.container) ))
		else:
#			sw.define_var('container','%shlp'%e.first.name,'new %shlp(_pair.key as HashMap)'%(e.first.name) )
			sw.writeln('%shlp _c(*(%s *) &(_itr->first) );'%(e.first.name,e.first.getMappingTypeName(e.container)))
		sw.writeln('_c.marshall(d);')
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var('&k',e.first.getMappingTypeName(e.container),'*(%s *) &(_itr->first)'%e.first.getMappingTypeName(e.container) )
		sw.writeln("k.marshall(d);")
		sw.scope_end()

	if isinstance( e.second,Builtin):
		sw.scope_begin()
		sw.define_var('v',e.second.getMappingTypeName(e.container),'_itr->second')
		Builtin_Python.serial(e.second.type,'v',idt,sw)
		sw.scope_end()
	elif isinstance( e.second,Sequence) or isinstance(e.second,Dictionary):
		sw.scope_begin()
		if isinstance(e.second,Sequence):
			sw.writeln('%shlp _c( *(%s*)&(_itr->second) );'%(e.second.name,e.second.getMappingTypeName(e.container)))
#			sw.define_var('container','%shlp'%e.second.name,'new %shlp(_pair.value as Array)'%(e.second.name) )
		else:
			sw.writeln('%shlp _c( *(%s*)&(_itr->second) );'%(e.second.name,e.second.getMappingTypeName(e.container)))
#			sw.define_var('container','%shlp'%e.second.name,'new %shlp(_pair.value as HashMap)'%(e.second.name) )
		sw.writeln('_c.marshall(d);')
		sw.scope_end()
	else:
		sw.scope_begin()
		sw.define_var('&v',e.second.getMappingTypeName(e.container),'*(%s *)&(_itr->second)'%e.second.getMappingTypeName(e.container) )
		sw.writeln("v.marshall(d);")
		sw.scope_end()
	sw.scope_end() # end for
	sw.scope_end() # end function
	sw.wln()

	#def unmarshall()
	sw.writeln("// unmarshall()")
	sw.writeln('bool unmarshall(tce::ByteArray& d){').idt_inc()
	sw.writeln("bool r = false;")
	sw.writeln("try{").idt_inc()
	sw.define_var("_size","size_t","0")
	sw.writeln("_size = d.readUnsignedInt();")


	sw.writeln("for(size_t _p=0;_p < _size;_p++){").idt_inc()

	if isinstance(e.first,Builtin):
		sw.define_var("_k",e.first.getMappingTypeName(e.container),e.first.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.first.type,'_k','d',sw.idt,sw)
	elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
		sw.define_var("_k",e.first.getMappingTypeName(e.container) )
		sw.define_var('_c1(_k)','%shlp'%e.first.name)
		sw.writeln('r = _c1.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_k",e.first.getMappingTypeName(e.container))
		sw.writeln('r = _k.unmarshall(d);')
		sw.writeln('if(!r) return false;')

	if isinstance(e.second,Builtin):
		sw.define_var("_v",e.second.getMappingTypeName(e.container),e.second.getTypeDefaultValue(e.container) )
		Builtin_Python.unserial(e.second.type,'_v','d',sw.idt,sw)
	elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
		sw.define_var("_v",e.second.getMappingTypeName(e.container) )
		sw.define_var('_c2(_v)','%shlp'%e.second.name)
		sw.writeln('r = _c2.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_v",e.second.getMappingTypeName(e.container))
		sw.writeln('r = _v.unmarshall(d);')
		sw.writeln('if(!r) return false;')


	sw.writeln("this->ds[_k] = _v;")
	sw.scope_end() # end for
	sw.idt_dec()
	sw.wln()
	sw.writeln('r = true;')
	sw.writeln('}catch(...){').idt_inc()
	sw.writeln('return false;')
	sw.scope_end()

	
	sw.writeln('return true;')
	sw.scope_end()	# end function

	sw.struct_end() # end class
	sw.writeln('//-- end Dictonary Class definations --')
	sw.wln()


'''
1.创建 接口类 （服务端dispatch 目标）
2.创建 接口代理类 prx
'''

def createAsyncCallBack(e,sw):
	sw.writeln('class %sPrx;'%e.getName() )
	sw.writeln('class %s_AsyncCallBack: public tce::RpcAsyncCallBackBase{'%e.getName()).idt_inc()
	sw.idt_dec().writeln('public:').idt_inc()
	#sw.writeln('virtual ~%s_AsyncCallBack(){}
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index

		if m.type.name == 'void':
			continue
		sw.writeln('virtual void %s(const %s & result,%sPrx* prx){'%(m.name,m.type.getMappingTypeName(e.container),e.getName() ) ).idt_inc()

		sw.scope_end().wln()
	sw.struct_end()
	sw.wln()

def createFunc_AsyncParserHlp(e,sw,m,idx,ifidx,opidx):
	sw.wln()
	#------------ AsyncParser_hlp  ---------
	if m.type.name =='void': # void 返回类型不能异步
		return
	sw.writeln('private:')
	sw.writeln('static void %s_asyncparser_hlp(tce::RpcMessage* m,tce::RpcMessage* m2){'%m.name).idt_inc()
#	sw.define_var('pthis','%sPtr*'%e.getName(),'(%sPtr*)prx'%e.getName())
	sw.define_var('pthis','%sPrx*'%e.getName(),'(%sPrx*)m->prx'%e.getName() )
	sw.writeln('pthis->%s_asyncparser(m,m2);'%m.name)
	sw.scope_end().wln()

def createFunc_AsyncParser(e,sw,m,idx,ifidx,opidx):
	sw.wln()
	sw.writeln('private:')
	
	idt = sw.idt
	#------------ AsyncParser  ---------
	if m.type.name =='void': # void 返回类型不能异步
		return

	# -- 生成 异步调用 函数返回值 解析的函数 ，静态函数
	sw.writeln('void %s_asyncparser(tce::RpcMessage* m_,tce::RpcMessage* m2_){'%(m.name,) ).idt_inc()
	sw.writeln("//# function index: %s , m2 - callreturn msg."%idx).wln() #stream,user,prx)
	sw.writeln('tce::RpcMessage* m = m_;')
	sw.writeln('tce::RpcMessage* m2 = m2_;')

	if m.type.name !='void':
		sw.define_var('stream','tce::ByteArray&','m2->paramstream')

		sw.define_var('user','%s_AsyncCallBack*'%e.getName(),'(%s_AsyncCallBack*)'%e.getName()+'m->async')
		#出现异常，不进行提示，！！ 也许应该讲错误信息传递给异步接收函数
		#有异常根本不会跑进这里

		#void 类型调用返回

		sw.writeln("if(stream.size() == 0){ ").idt_inc() #参数为空，表示return is 'void'
#		sw.writeln("user->%s(this);"%m.name) # void return
		sw.writeln("return;")
		sw.scope_end()

		sw.writeln("try{").idt_inc()
		#
		sw.define_var('d','tce::ByteArray')
		sw.writeln("d = stream;")
		#			sw.define_var('r','Boolean','true')

		if isinstance(m.type,Builtin):
			sw.define_var('_p',m.type.getMappingTypeName(e.container),m.type.getTypeDefaultValue(e.container))
			Builtin_Python.unserial(m.type.type,'_p','d',idt,sw)
		elif isinstance(m.type,Sequence):
			sw.define_var('_p',m.type.getMappingTypeName(e.container))
			sw.define_var('_c(_p)','%shlp'%m.type.name)
			sw.writeln(' _c.unmarshall(d);')
		elif isinstance(m.type,Dictionary):
#			sw.define_var('_p','HashMap','new HashMap()')
			sw.define_var('_p',m.type.getMappingTypeName(e.container))
#			sw.define_var('_c','%shlp'%m.type.name,'new %shlp(_p)'%m.type.name)
			sw.define_var('_c(_p)','%shlp'%m.type.name)
			sw.writeln('_c.marshall(d);')
		else:
			sw.define_var('_p',m.type.name)
			sw.writeln('_p.unmarshall(d);')
		#			sw.writeln("if(!r){ user(_p,this); }")
		sw.writeln('user->%s(_p,this);'%m.name)

		sw.idt_dec()
		sw.writeln("}catch(const tce::RpcException& e){").idt_inc()
		sw.writeln('tce::RpcCommunicator::instance().logTrace(e.what());')
		sw.scope_end()

	sw.scope_end() # end for function

	sw.wln()



def createFunc_Twoway(e,sw,m,idx,ifidx,opidx):
	params=[]
	list =[]
	idt = sw.idt

	sw.writeln('public:')
	sw.wln()
	for p in m.params:
	#			params.append( p.id,p.type.getMappingTypeName())
		list.append('%s %s'%(p.type.getMappingTypeName(e.container),p.id) )
	s = string.join( list,',')
	# 函数定义开始
	if s: s = s + ','

	oneway = ',bool oneway=false'
	type = 'void'
	if m.type.name !='void':
		type = m.type.getMappingTypeName(e.container)
		oneway='' #返回类型不为void，不能声明oneway


	#阻塞或者超时调用
	sw.writeln('%s %s(%sunsigned int timeout = 0,const tce::RpcProperites_t& props=tce::RpcProperites_t()) throw(tce::RpcException){'%(type,m.name,s) ).idt_inc()

	sw.writeln("//# function index: %s"%idx).wln()

	sw.define_var('m(new tce::RpcMessageCall(tce::RpcMessage::TWOWAY))','boost::shared_ptr<tce::RpcMessageCall>')

	sw.writeln("m->ifidx = %s;"%ifidx)
	sw.writeln("m->opidx = %s;"%opidx)
	sw.writeln('m->timeout = timeout;')
	sw.writeln('m->issuetime = tce::RpcCommunicator::instance().currentTimeStamp(); ') # 用于垃圾回收判别回收时间
	sw.writeln("m->paramsize = %s;"%len(m.params) )
	sw.writeln('m->call_id = tce::RpcCommunicator::instance().localServiceId();')
	sw.writeln('m->extra.set(props);')
	#默认为 twoway
	#sw.writeln('m->calltype = tce::RpcMessage::')

	sw.define_var('_d(new tce::ByteArray)','boost::shared_ptr<tce::ByteArray>')
	sw.define_var('d','tce::ByteArray&','*_d')

	for p in m.params:
		if isinstance(p.type,Builtin):
#			Builtin_Python.serial(p.type.type,p.id,idt,sw,'(*_d)')
			Builtin_Python.serial(p.type.type,p.id,idt,sw,'(d)')
		elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		elif isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		else:
			sw.writeln("%s.marshall(*_d);"%p.id)
#		sw.writeln("m->addParam(_d);")
	sw.writeln("m->paramstream.writeBytes(*_d);")
	sw.writeln("m->prx =(RpcProxyBase*)this;")
	sw.writeln('m->conn = this->conn;')
	#sw.writeln("m->wait = boost::shared_ptr< tce::MutexObject< tce::RpcMessage> >( new tce::MutexObject< tce::RpcMessage> );")

	sw.writeln("if( !this->conn->sendMessage(m) ){").idt_inc()
	sw.writeln('throw  tce::RpcException(tce::RpcConsts::RPCERROR_SENDFAILED);')
	sw.scope_end()
	#等待返回 超时
	sw.writeln('boost::shared_ptr<tce::RpcMessage> mr = m->wait->waitObject(timeout);')
	sw.writeln('if(m->exception.get()){').idt_inc()
	sw.writeln('throw *m->exception;') # 1. 网络丢失 ； 2. 远端异常错误返回
	sw.scope_end()

	sw.writeln('if(!mr.get()){').idt_inc() #超时异常
	sw.writeln('throw tce::RpcException(tce::RpcConsts::RPCERROR_TIMEOUT);')
	sw.scope_end()


	if m.type.name =="void":
		sw.writeln('d.size();')
		sw.writeln('return ;')
	else:
		sw.writeln('d = mr->paramstream;')
		if isinstance(m.type,Builtin):
			sw.define_var('p',m.type.getMappingTypeName(e.container))
			Builtin_Python.unserial(m.type.type,'p','d',idt,sw)
		elif isinstance(m.type,Sequence):
			sw.define_var('p',m.type.getMappingTypeName(e.container))
			sw.define_var('_c(p)','%shlp'%m.type.name)
			sw.writeln('_c.unmarshall(d);')
		elif isinstance(m.type,Dictionary):
			sw.define_var('p',m.type.getMappingTypeName(e.container))
			sw.define_var('_c(p)','%shlp'%m.type.name)
			sw.writeln('_c.unmarshall(d);')
		else:
			sw.define_var('p',m.type.name)
			sw.writeln('p.unmarshall(d);')

		sw.writeln('return p;')

	sw.scope_end()
#end --


def createFunc_Oneway(e,sw,m,idx,ifidx,opidx):
	params=[]
	list =[]
	idt = sw.idt
	sw.writeln('public:')
	sw.wln()
	for p in m.params:
		list.append('%s %s'%(p.type.getMappingTypeName(e.container),p.id) )
	s = string.join( list,',')
	# 函数定义开始
	if s: s = s + ','

#	if m.type.name =='void':
#		return
#		type = m.type.getMappingTypeName()
#		oneway='' #返回类型不为void，不能声明oneway

	#阻塞或者超时调用
	sw.writeln('void %s_oneway(%sconst tce::RpcProperites_t& props=tce::RpcProperites_t()) throw(tce::RpcException){'%(m.name,s) ).idt_inc()
	sw.writeln("//# function index: %s"%idx).wln()
	sw.define_var('m(new tce::RpcMessageCall( tce::RpcMessage::ONEWAY) )',
					'boost::shared_ptr<tce::RpcMessageCall>')

	sw.writeln("m->ifidx = %s;"%ifidx)
	sw.writeln("m->opidx = %s;"%opidx)
#	sw.writeln('m->timeout = timeout;')
	sw.writeln('m->issuetime = tce::RpcCommunicator::instance().currentTimeStamp(); ') # 用于垃圾回收判别回收时间

	sw.writeln("m->paramsize = %s;"%len(m.params) )
	sw.writeln('m->call_id = tce::RpcCommunicator::instance().localServiceId();')
	sw.writeln('m->extra.set(props);')
	if len(m.params):	
		sw.define_var('_d(new tce::ByteArray)','boost::shared_ptr<tce::ByteArray>')
		#sw.define_var('d','tce::ByteArray&','*_d')

	for p in m.params:
		if isinstance(p.type,Builtin):
			Builtin_Python.serial(p.type.type,p.id,idt,sw,'(*_d)')
		elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		elif isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		else:
			sw.writeln("%s.marshall(*_d);"%p.id)
#		sw.writeln("m->addParam(_d);")
	if m.params:
		sw.writeln("m->paramstream.writeBytes(*_d);")

	sw.writeln("m->prx =(RpcProxyBase*)this;")
#	sw.writeln("this->conn->sendMessage(m);")
	sw.writeln("if( !this->conn->sendMessage(m) ){").idt_inc()
	sw.writeln('throw  tce::RpcException(tce::RpcConsts::RPCERROR_SENDFAILED);')
	sw.scope_end()

	sw.scope_end()
#end --

def createFunc_Async(e,sw,m,idx,ifidx,opidx):
	params=[]
	list =[]
	idt = sw.idt
	
	if m.type.name =='void': # void 返回类型不能异步
		return
	sw.writeln('public:')
	sw.wln()
	for p in m.params:
		list.append('%s %s'%(p.type.getMappingTypeName(e.container),p.id) )
	s = string.join( list,',')
	# 函数定义开始
	if s: s = s + ','

	#阻塞或者超时调用
	sw.writeln('void %s(%s%s_AsyncCallBack* async,const tce::RpcProperites_t& props=tce::RpcProperites_t()) throw(tce::RpcException){'%(m.name,s,e.name) ).idt_inc()
	sw.writeln("//# function index: %s"%idx).wln()
	sw.define_var('m(new tce::RpcMessageCall(tce::RpcMessage::ASYNC))','boost::shared_ptr<tce::RpcMessageCall>')

	sw.writeln("m->ifidx = %s;"%ifidx)
	sw.writeln("m->opidx = %s;"%opidx)
	sw.writeln('m->issuetime = tce::RpcCommunicator::instance().currentTimeStamp(); ') # 用于垃圾回收判别回收时间
	sw.writeln("m->paramsize = %s;"%len(m.params) )
	sw.writeln('m->call_id = tce::RpcCommunicator::instance().localServiceId();')
	sw.writeln('m->extra.set(props);')
	if len(m.params):
		sw.define_var('_d(new tce::ByteArray)','boost::shared_ptr<tce::ByteArray>')
		#sw.define_var('d','tce::ByteArray&','*_d')

	for p in m.params:
		if isinstance(p.type,Builtin):
			Builtin_Python.serial(p.type.type,p.id,idt,sw,'(*_d)')
		elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		elif isinstance(p.type,Dictionary):
			v = sw.newVariant('_c')
			sw.define_var('%s(%s)'%(v,p.id),'%shlp'%p.type.name)
			sw.writeln('%s.marshall(*_d);'%v)
		else:
			sw.writeln("%s.marshall(*_d);"%p.id)
#		sw.writeln("m->addParam(_d);")
	if m.params:
		sw.writeln("m->paramstream.writeBytes(*_d);")
	sw.writeln("m->prx =(tce::RpcProxyBase*)this;")
	sw.writeln("m->async = async;")
	sw.writeln("m->callback = %sPrx::%s_asyncparser_hlp;"%(e.getName(),m.name) )
	sw.writeln("m->conn = this->conn;")
#	sw.writeln("async->synchlp = %sPrx::%s_asyncparser_hlp;"%(e.getName(),m.name))
#	sw.writeln("this->conn->sendMessage(m);")

	sw.writeln("if( !this->conn->sendMessage(m) ){").idt_inc()
	sw.writeln('throw  tce::RpcException(tce::RpcConsts::RPCERROR_SENDFAILED);')
	sw.scope_end()


	sw.scope_end()
#end --


def createServantDelegate(e,sw,idx,ifidx):
	idt = sw.idt
	sw.classfile_enter("%s_delegate"%e.getName())
	sw.wln()
	#服务对象调用委托
	sw.writeln("class %s_delegate:public tce::RpcServantDelegate {"%e.getName()).idt_inc()

	sw.wln()

	sw.writeln('public:')
#	sw.writeln('typedef boost::function<bool (tce::RpcContext&)> call_type;')
#	sw.writeln('std::map<int,call_type > optlist;')
	sw.writeln('%s * inst;'%e.getName())
	sw.wln()
#	sw.writeln("%s_delegate(%s* inst,boost::shared_ptr< tce::CommAdapter>& adapter, "
#			   "boost::shared_ptr< tce::RpcConnection> >& conn){"
#	%(e.getName(),e.getName() )
#	).idt_inc()

	sw.writeln("%s_delegate(%s* inst){"%(e.getName(),e.getName() )).idt_inc()

	#	sw.writeln("this.adapter = adapter;")
	sw.writeln('this->_index = %s;'%ifidx)

	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.writeln("this->_optlist[%s] = &%s_delegate::%s_dummy;"%(opidx,e.getName(),m.name)) #直接保存 twoway 和 oneway 函数入口

	sw.writeln("this->inst = inst;")
	sw.scope_end().wln()

	#开始委托 函数定义
	for opidx,m in enumerate(e.list): # function list
		opidx = m.index
		sw.writeln('static bool %s_dummy(tce::RpcContext& ctx){'%(m.name) ).idt_inc()
		sw.writeln('%s_delegate *pf = (%s_delegate*) ctx.delegate;'%(e.getName(),e.getName()))
		sw.writeln('return pf->%s(ctx);'%m.name)
		sw.scope_end().wln()

		sw.writeln('bool %s(tce::RpcContext& ctx){'%(m.name) ).idt_inc()

		params=[ ]
		sw.define_var('d','tce::ByteArray&','ctx.msg->paramstream')
		sw.writeln('d.size();')
		#		sw.writeln("d = ctx.msg.paramstream; ")
		sw.writeln('bool r = false;')
		#sw.writeln("idx = 0")
		#防止参数重命名，加上 _p_前缀
		sw.writeln('r = false;')
		for p in m.params:
			if isinstance(p.type,Builtin):
				
				sw.define_var(p.id,p.type.getMappingTypeName(e.container))
				Builtin_Python.unserial(p.type.type,p.id,'d',idt,sw)
			elif isinstance(p.type,Sequence) or isinstance(p.type,Dictionary):
				sw.define_var(p.id,p.type.getMappingTypeName(e.container))
				sw.scope_begin()
				sw.define_var('_c(%s)'%p.id,'%shlp'%p.type.name)
				sw.writeln('r = _c.unmarshall(d);')
				sw.writeln('if(!r) return false;')
				sw.scope_end()

			else:
				sw.define_var(p.id,p.type.getMappingTypeName(e.container))
				sw.writeln('r = %s.unmarshall(d);'%p.id)
				sw.writeln('if(!r) return false;')

			params.append(p.id)
		#params = map( lambda x: '_p_'+x,params)
		ps = string.join(params,',')

		if ps: ps = ps + ','
		#		sw.define_var('servant',e.getName(),'this.inst as %s'%e.getName())
		if isinstance(m.type,Builtin) and m.type.type =='void':
			sw.writeln("this->inst->%s(%sctx);"%(m.name,ps) )
		else:
			sw.define_var('cr',m.type.getMappingTypeName(e.container))
			sw.writeln("cr = this->inst->%s(%sctx);"%(m.name,ps) )

		sw.writeln("if( ctx.msg->calltype & tce::RpcMessage::ONEWAY){").idt_inc()
		sw.writeln("return false;")
		sw.scope_end()

		sw.wln()

		sw.define_var('_d(new tce::ByteArray)','boost::shared_ptr<tce::ByteArray>')
		#sw.define_var('d','tce::ByteArray&','*_d')
		#sw.writeln('d = *_d;')
		sw.define_var('m(new tce::RpcMessageReturn)','boost::shared_ptr<tce::RpcMessageReturn>')
		sw.writeln("m->sequence = ctx.msg->sequence;") #返回事务号与请求事务号必须一致
		sw.writeln("m->ifidx = ctx.msg->ifidx;")
		sw.writeln("m->call_id = ctx.msg->call_id;")
		sw.writeln("m->conn = ctx.conn;")
		sw.writeln('m->callmsg = ctx.msg;')

		if isinstance( m.type ,Builtin ):
			Builtin_Python.serial(m.type.type,'cr',idt,sw,'(*_d)')

		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			sw.scope_begin()
			v = sw.newVariant('_c')
			sw.define_var('%s(cr)'%v,'%shlp'%m.type.name)
			sw.writeln('%s.marshall( *_d );'%v)
			sw.scope_end()
		else:
			sw.writeln("cr.marshall( *_d );")

		sw.writeln("m->paramstream.writeBytes(*_d);")
#		sw.writeln("if(_d->size()) m->addParam(_d);")
		sw.writeln("ctx.conn->sendMessage(m);")
		sw.writeln("return true;")

		sw.scope_end()
		sw.wln()
	sw.struct_end()
	sw.classfile_leave()

def createServant(e,sw,idx,ifidx):
	global  gbufwriter
	idt = sw.idt
	sw.classfile_enter(e.getName())
	sw.wln()
#	sw.writeln('class %s_delegate;'%e.getName() ).wln()
#	sw.writeln('class %s:public tce::RpcServant,public boost::enable_shared_from_this<%s>{'%(e.getName(),e.getName()) )
	sw.writeln('class %s:public tce::RpcServant{'%(e.getName()) )
	sw.idt_inc()
	sw.writeln("//# -- INTERFACE -- ")
#	sw.writeln("~%s(){}"%e.getName() ).idt_inc()
	sw.writeln('public:').wln()
	sw.writeln("boost::shared_ptr<%s_delegate> delegate;"%e.getName())
	#写入对应的delegate 类对象

	sw.writeln("%s();"%(e.getName(),) )
#	sw.writeln('this.delegate = boost::shared_ptr<%s_delegate>( new %s_delegate(this) );'%(e.getName(),e.getName() ))

#	sw.scope_end()
	sw.wln()

	pkg = sw.pkg_current()
	gbufwriter.wln().idt_inc()

	gbufwriter.writeln("inline %s::%s(){"%(e.getName(),e.getName()) ).idt_inc()
	gbufwriter.writeln('this->_delegate = boost::shared_ptr<%s_delegate>( new %s_delegate(this) );'%(e.getName(),e.getName() ))
#	gbufwriter.writeln('this.delegate = new %s_delegate(this) ;'%(e.getName(),e.getName() ))
	gbufwriter.scope_end().wln()


#	sw.writeln("%s(){"%e.getName() ).idt_inc()
#	sw.writeln('this.delegate = boost::shared_ptr<%s_delegate>( new %s_delegate(this) );'%(e.getName(),e.getName() ))
#	sw.scope_end().wln()

	for m in e.list: # function list
		sw.wln()
		params=[]
		for p in m.params:
			params.append( (p.id,p.type.getMappingTypeName(e.container)) )
		list =[]
		for v,t in params:
			list.append('const %s& %s'%(t,v))
		s = string.join( list,',')
		if s: s += ','
		#		retype = 'std::map<%s,%s>'%m.type.first
		sw.writeln('virtual %s %s(%stce::RpcContext& ctx){'%(m.type.getMappingTypeName(e.container) ,m.name,s) ).idt_inc()
		#------------定义默认返回函数----------------------

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

	sw.struct_end() # end class


	sw.classfile_leave()

#	sw.writeln("typedef boost::shared_ptr<%s> %sPtr;"%(e.getName(),e.getName()) )

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
	ifidx = ifcnt
	ifcnt+=1


	import tce_util
	ifname = "%s.%s"%(e.container.name,e.name)
	r = tce_util.getInterfaceIndexWithName(ifname)
	# print 'get if-index:%s with-name:%s'%(r,ifname)
	if r != -1:
		ifidx = r

	e.ifidx = ifidx

	interface_defs[ifidx] = {'e':e,'f':{}}

	fileifx.write('<if id="%s" name="%s"/>\n'%(ifidx,e.name))
	fileifx.flush()


	tce_util.rebuildFunctionIndex(e)


	expose = tce_util.isExposeDelegateOfInterfaceWithName(ifname)


	# if e.delegate_exposed:
	if expose:
		sw.writeln('class %s_delegate;'%e.getName())
		createServant(e,sw,idx,ifidx)
		createServantDelegate(e,sw,idx,ifidx)
	# -----------  RpcAsyncCallBackBase ---------------
	createAsyncCallBack(e,sw)
	# ----------- END RpcAsyncCallBackBase ---------------
	sw.wln()

	sw.writeln("typedef boost::shared_ptr<%sPrx> %sPrxPtr;"%(e.getName(),e.getName()) )

	sw.writeln('class %sPrx: public tce::RpcProxyBase{'%e.getName() ).idt_inc()
	sw.writeln("//# -- INTERFACE PROXY -- ")
#	sw.writeln('var conn:RpcConnection ;')

	#sw.writeln('void* delta;')
	sw.writeln('public:')
	sw.wln()
	sw.writeln('%sPrx(){}'%e.getName())
	sw.writeln("%sPrx( boost::shared_ptr<tce::RpcConnection> & conn){"%(e.getName())).idt_inc()
	sw.writeln("this->conn = conn;")
	sw.scope_end()

	sw.writeln('~%sPrx(){ if(this->conn.get()){ this->conn->close();}}'%e.getName())
	sw.writeln('public:').wln()
#	sw.writeln('boost::shared_ptr<tce::RpcConnection>  conn')

	for opidx,m in enumerate(e.list): # function list
		opidx = m.index

		sw.wln()
		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象

		createFunc_Twoway(e,sw,m,idx,ifidx,opidx)
		createFunc_Async(e,sw,m,idx,ifidx,opidx)
		createFunc_Oneway(e,sw,m,idx,ifidx,opidx)
		createFunc_AsyncParserHlp(e,sw,m,idx,ifidx,opidx)
		createFunc_AsyncParser(e,sw,m,idx,ifidx,opidx)
		
	sw.writeln('public:')
	sw.writeln('static %sPrxPtr create(tce::RpcConnectionPtr& conn){'%(e.getName()) ).idt_inc()
	sw.writeln('return %sPrxPtr( new %sPrx(conn) );'%(e.getName(),e.getName() ))
	sw.scope_end()
	
	sw.wln()
	
	#异步连接始终返回true,除非uri参数格式错误，之后需要通过 connection::isConnected()去检测状态
	sw.writeln('// async 返回的链接状态 ')
	sw.writeln('static %sPrxPtr create(const std::string& uri,tce::RpcConnection::Types conntype=tce::RpcConnection::SOCKET, bool sync=false,const tce::Properties_t& props = tce::Properties_t()){'%(e.getName()) ).idt_inc()
	sw.writeln('tce::RpcConnectionPtr conn ;')
	sw.writeln('conn = tce::RpcCommunicator::instance().createConnection(conntype,uri,props);')
	sw.writeln('bool r = false;')
	sw.writeln('r = conn->connect();')
	sw.writeln('if(!r) return %sPrxPtr();'%e.getName()) 
	
	sw.writeln('return %sPrxPtr( new %sPrx(conn) );'%(e.getName(),e.getName() ))
	sw.scope_end()
	

	sw.struct_end() # end class  '};'
#	sw.classfile_leave()


	# --  begin 异步调用 ---

	# --  end 异步调用 ---



	return
#
'''
伪代码

def

'''


def createCodeInterfaceMapping():
	global interface_defs # {e,f:{}}
	pass




def createCodeFrame(e,idx,sw ):
	idt = Indent()



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

class Buffer:
	def __init__(self):
		self.d = ''

	def write(self,s):
		self.d+=s

	def close(self):
		self.d=''

# if iflist is null means all interface is requred
#
def unique_append(list,new):
	for e in list:
		if e.name == new.name:
			return
	list.append(new)

def filterStruct(final,list):
	structs=[]
	for e in final:
		if not isinstance(Struct):
			continue
		structs.append(e)


def filterInterface(unit,iflist):
	global  ifcnt

	if not iflist:
		return
	ifx = []
	types=[]
	types2=[]

	for idx,e in enumerate(unit.list):
		if not isinstance(e,Interface):
			ifx.append(e)
			continue
		e.ifidx = ifcnt
		ifcnt+=1

		if not iflist.count(e.getName()):
			continue
		for m in e.list:
			for p in m.params: # check params of function
				for e2 in unit.list:
					if e2.name == p.type.name:
						unique_append(types,e2)

			#check return param
			for e2 in unit.list:
				if m.type.name == e2.name:
					unique_append(types,e2)
			#
		ifx.append(e)

	for e2 in types:
		searchTypes(e2,unit.list,types2)

	types3 = ifx + types + types2

	all =[]
	for e in unit.list:
		for e2 in types3:
			if e.name == e2.name:
				unique_append(all,e)
#	print all

	unit.list = all

def searchTypes(e,list,result):
	unique_append(result,e)
	if isinstance(e,Struct):
		for e2 in e.list:
			if not isinstance(e2,Builtin):
				searchTypes(e2,list,result)
	if isinstance(e,Sequence):
		if not isinstance(e.type,Builtin):
			searchTypes(e.type,list,result)


def createCodes():
	#file = sys.argv[1]

	global  interface_defs,ifcnt

	file = ''

	ostream = Outputer()
#	ostream.addHandler(sys.stdout)

	argv = sys.argv
	outdir ='.'
	outfile =''
	filters=''
	while argv:
		p = argv.pop(0)
		if p =='-o':
			p = argv.pop(0)
			outfile = p

		if p =='-i':
			if argv:
				p = argv.pop(0)
				file = p

		if p =='-if': # 接口起始下标，如多个module文件并存，则同坐此参数区分开
			if argv:
				ifcnt = int(argv.pop(0))

		#过滤，仅仅生成指定的接口代码
		# 接口名称以空格分隔
		# 接口名称尾部添加 + - 表示是否生成接口的服务器实现代码
		# "A+,B-,C-,D"
		# 未有+ - 默认为+
		if p =='-filter':
			if argv:
				filters = argv.pop(0)



	fp = open(file,'r')
	content = fp.read()
	fp.close()

	#默认采用idl文件名称
	if not outfile:
		outfile = file

	path  = os.path.dirname(outfile)
	name = os.path.basename(outfile).split('.')[0]



	sw = StreamWriter()

	txt='''
#include <string>
#include <functional>
#include <map>
#include <vector>
#include <list>
#include <algorithm>
#include <boost/smart_ptr.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <tce/tce.h>
//#include "/root/workspace/tce/code/cpp/tce/tce.h"
//#include "/Users/socketref/Documents/workspace/test2/src/tce2.h"

'''
	sw.setIncludes('default',(txt,))
#	print name,',' ,path
	sw.createPackage(name,path)
	sw.pkg_enter(name)

#	ostream.write(headtitles)
	unit = syntax_result(content)

	# filters = [ x for x in map(string.strip,filters.split(' ')) if x]
	# import tce_util
	# tce_util.filterInterface(unit,filters,ifcnt)

	for module in global_modules:
		name = module.name
		print 'module:',name,module.ref_modules.keys()
		# print module.children

		for idx,e in enumerate(module.list):
			createCodeFrame(e,idx,sw)
			ostream.write(NEWLINE)
	#inline wroten
	sw.write(gbufwriter.ostream.d)
	sw.pkg_leave()



class LanguageCPlusPlus(object):
	language = 'cpp'
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
				r ='unsigned char'
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
				if lexparser.arch =='32':
					r = 'long long'
			elif type in ('double',):
				r = 'double'
			elif type in ('string',):
				r = "std::string"
			elif type in ('void',):
				r ='void'
			return r

	class Sequence:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'std::vector< %s >()'%this.type.getMappingTypeName(call_module)

		@classmethod
		def typeName(cls,this,call_module):

			return 'std::vector< %s >'%this.type.getMappingTypeName(call_module)


	class Dictionary:
		@classmethod
		def defaultValue(cls,this,call_module):
			return 'std::map< %s,%s >()'%(this.first.getMappingTypeName(call_module),
											 this.second.getMappingTypeName(call_module)
											)

		@classmethod
		def typeName(cls,this,call_module):
			return 'std::map< %s,%s >'%(this.first.getMappingTypeName(call_module),
									this.second.getMappingTypeName(call_module) )


	class Struct:
		@classmethod
		def defaultValue(cls,this,call_module):
			return '%s()'%this.getTypeName(call_module)

		@classmethod
		def typeName(cls,this,call_module):
			r = this.name
			if this.module:
				r = '%s::%s'%(this.module,this.name)
			return r

	class Module:
		def __init__(self,m):
			self.m = m

lexparser.language = 'cpp'
lexparser.arch = '64' # 64位操作系统

lexparser.lang_kws = ['for', 'namespace','float',
					  'new', 'class',  'public','protected','private','struct',
					  'while', 'do', 'virtual','throw',]

lexparser.codecls = LanguageCPlusPlus

if __name__ =='__main__':
	createCodes()


	'''
	tce2cpp.py -i idl -o output.h

	'''

#	a=[10,20]
#	t = TA(a)
#	t.test()
#	print a


