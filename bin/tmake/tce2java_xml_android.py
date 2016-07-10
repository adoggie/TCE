#--coding:utf-8--

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
# revision:
# 2012.11.14 scott
# 1.支持android异步线程模式
# 2.调用模式 oneway,async 两种
# 3.异步模式回调事件： onResult(),onError()


'''
java_xml 包装限制
不支持 dictionary
sequence不支持简单数据类型的数组
TC不返回消息的类型，调用时请使用oneway方式调用
不允许  <xml>abc</xml> 这种数据方式 以 <xml id="abc"/>替代
调用返回值不能是简单数据类型，必须以struct包装,除了void类型:
<NaviMSG>
	<result code="0"/>
</NaviMSG>



sequence >> xml:

idl:
	struct if_op_p_item_t{
		string id;
		string name;
	};
	sequence<item> if_op_p_dataset_t;
xml:
	<dataset>
	  <item id="100" name="mechine"/>
	  <item id="101" name="aircraft"/>
	  ....
	</dataset>

struct 命名格式：
	struct if_op_p_item_t{}

	if - 接口名称,类名称
	op - 接口内部的方法名称
	item- xml的nodeTagName
 以下划线_分隔每个区域，故限定 接口、函数和xml节点名称不能包含下划线_




'''

import os
import os.path
import string
import traceback

import lexparser
from lexparser import *
from mylex import syntax_result




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

		if not  os.path.exists(name):
#			print 'mkdir:',name
			os.mkdir(name)

	#进入包空间
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
#		self.write("package %s"%pkg).brace1().wln().idt_dec()
#		print pkg
		self.idt.reset()
		self.write("package %s;"%pkg)

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

	@staticmethod
	def serial(typ,val,sw,xml,complexed=True):
		# typ - builtin object ; val - variant name; var = d
		s=''
		#make xml node attributes
		if typ.type in ('byte','short','int','long','float','double','string'):
			if complexed:
				sw.writeln('''%s+=String.format(" %s=\\"%%s\\"",%s.toString());'''%(xml,val,val) )
			else:
				sw.writeln('''%s+=String.format(" <%s>\\"%%s\\"<%s>",%s.toString());'''%(xml,val,val,val) )
		elif typ.type == 'bool':
			if complexed:
				sw.writeln("if(%s.booleanValue() == true){"%val).idt_inc()
				sw.writeln('''%s+=" %s=\"1\"";'''%(xml,val) ).idt_dec()
				sw.writeln("}else{").idt_inc()
				sw.writeln('''%s+=" %s=\"0\"";'''%(xml,val) )
				sw.scope_end()
			else:
				sw.writeln("if(%s.booleanValue() == true){"%val).idt_inc()
				sw.writeln('''%s+=" <%s>\"1\"<%s>";'''%(xml,val,val) ).idt_dec()
				sw.writeln("}else{").idt_inc()
				sw.writeln('''%s+=" <%s>\"0\"<%s>";'''%(xml,val,val) )
				sw.scope_end()
		return s

	@staticmethod
	def unserial(typ,val,xmlnode,sw,complexed=True):
		s=''
		if complexed:
			#从xml node读取attributes,如果不存在指定的属性，则取默认值 null
			sw.writeln("// if attr-name not existed, it return null-string ")
			sw.define_var(sw.newVariant('_b'),'String', "%s.getAttribute(\"%s\")"%(xmlnode,val) )

			if( typ.type =='void'):
				return

			#允许属性不存在
			sw.writeln('try{').idt_inc()

			if typ.type != 'bool':
	#
				sw.writeln("%s = %s.valueOf(%s);"%(val,typ.getMappingTypeName(),sw.lastvar))
			else: # 'bool'
				sw.writeln("if(%s==\"0\"){")%(sw.lastvar).idt_inc()
				sw.writeln("%s = Boolean.valueOf(true);"%(val))
				sw.writeln('}else{').idt_inc()
				sw.writeln("%s = Boolean.valueOf(false);"%(val))
				sw.scope_end()

			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('RpcCommunicator.instance().getLogger().info(e.getMessage());')
			sw.scope_end()
		else:
			if( typ.type =='void'):
				return
			sw.define_var(sw.newVariant('_b'),'String', "%s.getTextContent()"%(xmlnode,) )

			#允许属性不存在
			sw.writeln('try{').idt_inc()

			if typ.type != 'bool':
			#
				sw.writeln("%s = %s.valueOf(%s);"%(val,typ.getMappingTypeName(),sw.lastvar))
			else: # 'bool'
				sw.writeln("if(%s==\"0\"){")%(sw.lastvar).idt_inc()
				sw.writeln("%s = Boolean.valueOf(true);"%(val))
				sw.writeln('}else{').idt_inc()
				sw.writeln("%s = Boolean.valueOf(false);"%(val))
				sw.scope_end()

			sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
			sw.writeln('RpcCommunicator.instance().getLogger().info(e.getMessage());')
			sw.scope_end()
		return s

'''从类型名称获取XML数据中的Tag
tc_redirect_p_User_t 末尾的User,作为 <User>
'''
class GrammarXML:
	@staticmethod
	def extractXMLTag(name):
#		print type(name),name
#		if name.find('_') ==-1:
#			return name
		pp = name.split('_')
		if pp[-1] != 't':
#			return name
			print '1.invalid variable name:%s (must be  subfixed with _t)'%name
			traceback.print_exc()
			sys.exit()
		return pp[-2]
'''
	@staticmethod
	def extractXML_methodName(name): #获取函数名称
		pp = name.split('_')
		if pp[-1] != 't':
			print 'invalid variable name:%s (must be  subfixed with _t)'%name
			sys.exit()
		return pp[1]

	@staticmethod
	def extractXML_interfaceName(name): #获取接口名称
		pp = name.split('_')
		if pp[-1] != 't':
			print 'invalid variable name:%s (must be  subfixed with _t)'%name
			sys.exit()
		return pp[0]
'''
def createCodeStruct(e,sw,idt):
	#sw = StreamWriter(ostream,idt)
	sw.wln()
	params=[ ]
	for m in e.list:
#		v = m.type.getTypeDefaultValue()
		v = m.type.getMappingTypeName()
		params.append( (m.name,v) )
	pp =map(lambda x: '%s %s'%(x[1],x[0]),params)
	ps = string.join(pp,',')

	sw.writeln('import java.util.*;')
	sw.writeln('import java.util.HashMap;')
	l ='public class %s{'%e.getName()
	sw.writeln(l)
	sw.writeln("// -- STRUCT -- ")
	sw.idt_inc()
	sw.writeln('HashMap<String,String> http_params = new HashMap<String,String>();')
	for m in e.list:
		d = m.type.getTypeDefaultValue()
		v = m.type.getMappingTypeName()

		sw.writeln("public  %s %s = %s;"%(v,m.name,d))

	sw.wln()
	sw.writeln("//构造函数")
	sw.writeln('public %s(){'%(e.getName(),) )
	sw.idt_inc()
	sw.wln().idt_dec()
	sw.newline().brace2().wln()


	#定义序列化函数
	sw.wln()
	sw.writeln("// return xml string")
	sw.writeln('public String marshall(){').idt_inc()
	sw.define_var("xml","String" ,"new String()")
#	sw.define_var("str","String")


	sw.writeln("xml=\"<%s\";"% GrammarXML.extractXMLTag(e.name))
	sw.writeln("//不能当attr处理的复合成员")
	sw.writeln("Vector<String> complexes = new Vector<String>(); ")
	for m in e.list:

#		print m,m.name,m.type.type,m.type.name
		if isinstance(m.type,Builtin):
			Builtin_Python.serial(m.type, m.name,sw,'xml')
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
#			sw.scope_begin()
			v = sw.newVariant('_b')
			sw.writeln('%shlp %s = new %shlp(this.%s);'%(m.type.name,v,m.type.name,m.name) )
			sw.writeln('complexes.add(%s.marshall());'%v)
#			sw.writeln('complexes.add(str);')
#			sw.scope_end()
		else:
#			sw.scope_begin()
			sw.writeln("complexes.add( %s.marshall());"% m.name )
#			sw.writeln('complexes.add(str);')
#			sw.scope_end()
	#close xml brace
	sw.writeln('if(complexes.size() ==0 ){').idt_inc()
	sw.writeln("xml+=\"/>\";").idt_dec()
	sw.writeln('}else{').idt_inc()
	sw.writeln("for(String s:complexes){").idt_inc()
	sw.writeln("xml+=s;")
	sw.scope_end() # end for
	sw.writeln("xml=\"</%s>\\n\";"% GrammarXML.extractXMLTag(e.name))
	sw.scope_end() # end if
	sw.writeln("return xml;")
	sw.scope_end() # end function

	sw.wln()

	#---------------------------------------------------------------------
	#-- begin marshall_http() --
	# marshall_http_get() 仅仅支持发起调用传递参数的url包装
	# 数据必须是struct，且内部成员必须是简单数据类型
	# 如果要传递复杂数据类型，请使用POST请求
	# 返回数据格式必须是xml
	sw.writeln("// return  string")
	sw.writeln('public String marshall_http_get(){').idt_inc()
	sw.define_var("url","String" ,"new String()")

	for m in e.list:
		if isinstance(m.type,Builtin):
			#Builtin_Python.serial(m.type, m.name,sw,'xml')
#			sw.writeln('url+="%s=%s.toString()&";'%(m.name,m.name))
			sw.writeln('''url+=String.format("%s=%%s&",%s.toString());'''%(m.name,m.name) )
			sw.writeln('http_params.put("%s",%s.toString());'%(m.name,m.name))
		else:
			sw.writeln('//unsupported data,must be primitive type!')
	sw.writeln("return url;")
	sw.scope_end() # end function
	sw.wln()
	# -- end marshall_http_get() --
	#---------------------------------------------------------------------

	#unmarshall()
	sw.writeln("//反序列化 unmarshall()   parentNode 有时为null")
	sw.writeln("public boolean unmarshall(Element xmlnode,Element parentNode){" )

	sw.idt_inc()
	sw.writeln( "try{")
	sw.idt_inc()
	sw.define_var("r","boolean","false")
	# xmlnode 传递进来就是本节点，并不是指向父亲节点
	sw.writeln("if(parentNode!=null){").idt_inc()
	sw.define_var("nodes","NodeList","parentNode.getElementsByTagName(\"%s\")"%GrammarXML.extractXMLTag(e.name) )
	sw.writeln("if(nodes.getLength() == 0) return false;")	#即使 xml node不存在也返回true
	sw.writeln("xmlnode = (Element)nodes.item(0);").idt_dec() #找到自己的tagNonde
	sw.writeln('}else{').idt_inc()
	sw.writeln('if( !xmlnode.getTagName().equals("%s") ) return false;'%GrammarXML.extractXMLTag(e.name) )
	sw.scope_end()


	for m in e.list:
		if isinstance(m.type,Builtin):
			Builtin_Python.unserial(m.type,m.name,'xmlnode',sw)
		elif isinstance(m.type,Sequence) or isinstance(m.type,Dictionary):
			v = sw.newVariant('_b')
			sw.define_var(v,"%shlp"%m.type.name,"new %shlp(this.%s)"%(m.type.name,m.name) )
			sw.writeln("r = %s.unmarshall(null,xmlnode);"%v)
			#sw.writeln("if(!r){return false;}")
		else:
			sw.writeln('r = this.%s.unmarshall(null,xmlnode);'%m.name )
			#sw.writeln("if(!r){return false;}")

	sw.idt_dec()
	sw.writeln('}catch(Exception e){' )
	sw.idt_inc()
	sw.writeln('tce.RpcCommunicator.instance().getLogger().error(e.getMessage());')
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
	sw.writeln('import java.util.*;')

	sw.writeln('public class %shlp{'%e.getName() )
	sw.idt_inc()
	sw.writeln('//# -- SEQUENCE --')
#	sw.wln().writeln("public var ds:Array = null;")
	sw.wln()
	sw.writeln("public Vector<%s> ds = null;"%e.type.name )
	sw.writeln('public %shlp(Vector<%s> ds){'%(e.getName(),e.type.name) ).idt_inc()
	sw.writeln('this.ds = ds;')
	sw.scope_end().wln()

	sw.writeln("// xmlnode -> parent node ")
	sw.writeln('public String marshall(){').idt_inc()
	#先写入 数组封套
	sw.define_var('xml','String',"\"<%s>\""%GrammarXML.extractXMLTag(e.name))

#	sw.writeln("d.writeInt(this.ds.length);")

	sw.writeln('for(%s item : this.ds){'%e.type.name ).idt_inc()

	if isinstance( e.type,Builtin):
		Builtin_Python.serial(e.type.name,'item',sw,'xml',False) #要生成<age>100</age>
		#数组不能直接存储 原始数据类型 builtin_type
	elif isinstance(e.type,Sequence) or isinstance(e.type,Dictionary):
		v = sw.newVariant('_b')
		sw.define_var(v,'%shlp'%e.type.name,'new %shlp(item)'%(e.type.name) )
		sw.writeln('xml +=%s.marshall();'%v)

	else:
		sw.writeln("xml += item.marshall();")

	sw.scope_end()	#end for
	sw.writeln("xml +=\"</%s>\";"%GrammarXML.extractXMLTag(e.name))
	sw.writeln("return xml;")
	sw.scope_end() # end function
	sw.wln()
	#def unmarshall()

	sw.writeln('public boolean unmarshall(Element xmlnode,Element parentNode){').idt_inc()

	sw.writeln("try{").idt_inc()

	sw.define_var("r","boolean","false")

	sw.writeln("if(parentNode!=null){").idt_inc()
	sw.define_var("nodes","NodeList","parentNode.getElementsByTagName(\"%s\")"%GrammarXML.extractXMLTag(e.name) )
	sw.writeln("if(nodes.getLength() == 0) return false;")
	sw.writeln("xmlnode = (Element)nodes.item(0);").idt_dec() #找到自己的tagNonde
	sw.writeln('}else{').idt_inc()
	sw.writeln('if( !xmlnode.getTagName().equals("%s") ) return false;'%GrammarXML.extractXMLTag(e.name) )
	sw.scope_end()

	sw.define_var('nodes',"NodeList")
	sw.writeln('nodes = xmlnode.getElementsByTagName("%s");'%(GrammarXML.extractXMLTag(e.type.name)))

	sw.writeln("Element node;")
	sw.writeln("for(int _p=0;_p < nodes.getLength();_p++){").idt_inc()
	sw.writeln("node =(Element) nodes.item(_p);")
	sw.writeln('''if( !node.getTagName().equals("%s") ) continue; '''%(GrammarXML.extractXMLTag(e.type.name)))

	v = sw.newVariant('_b')
	if isinstance(e.type,Builtin): #无法包装直接的原始数据数组
		c = sw.newVariant('_b')
		sw.define_var(c,"%s"%e.type.getMappingTypeName())
		Builtin_Python.unserial(e.type,c,'node',sw.idt,sw,False)
		sw.writeln("this.ds.add(%s);"%c)
	#dictionary 不支持
	elif isinstance( e.type,Sequence) or isinstance(e.type,Dictionary):

		if isinstance( e.type,Sequence):
			sw.define_var(v,"Vector<%s>"%e.type.type.name,"new Vector<%s>()"%e.type.type.name)
		else:
			#sw.define_var("_o","HashMap","new HashMap()")
			pass
		c = sw.newVariant('_b')
		sw.define_var(c,"%shlp"%e.type.name,"new %shlp(%s)"%(e.type.name,c))
		sw.writeln("r = %s.unmarshall(%s,%s);"%(c,'null','node'))
		sw.writeln("if(!r) return false;")
		sw.writeln("this.ds.add(%s);"%v)

	else:

		sw.define_var(v,e.type.name,"new %s()"%e.type.name)
		sw.writeln("r= %s.unmarshall(node,null);"%v)
		sw.writeln("if(!r) return false;")
		sw.writeln("this.ds.add(%s);"%v)


	sw.scope_end() # end for{}

	sw.idt_dec()
	sw.writeln("}catch(Exception e){").idt_inc()
	sw.writeln('tce.RpcCommunicator.instance().getLogger().error(e.getMessage());')
	sw.writeln("return false;")
	sw.scope_end()

	sw.writeln("return true;")
	sw.scope_end() # end function

	sw.wln()
	sw.scope_end() # end class
	sw.wln()



def createCodeDictionary(e,sw,idt):

	sw.wln()
	sw.writeln('public class %shlp {'%e.getName() ).idt_inc()
	sw.writeln('//# -- THIS IS DICTIONARY! --')
	sw.writeln('public var ds :HashMap = null;').wln()
	sw.writeln('public function %shlp(ds:HashMap){'%e.getName() ).idt_inc()	#将hash数据{}传递进来
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
		sw.define_var('k',e.first.getMappingTypeName(),'_pair.key as %s'%e.first.getMappingTypeName())
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
		sw.define_var('k',e.first.getMappingTypeName(),'_pair.key as %s'%e.first.getMappingTypeName() )
		sw.writeln("k.marshall(d);")
		sw.scope_end()

	if isinstance( e.second,Builtin):
		sw.scope_begin()
		sw.define_var('v',e.second.getMappingTypeName(),'_pair.value as %s'%e.second.getMappingTypeName())
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
		sw.define_var('v',e.second.getMappingTypeName(),'_pair.value as %s'%e.second.getMappingTypeName())
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
		sw.define_var("_k",e.first.getMappingTypeName(),e.first.getTypeDefaultValue() )
		Builtin_Python.unserial(e.first.type,'_k','d',sw.idt,sw)
	elif isinstance(e.first,Sequence) or isinstance(e.first,Dictionary):
		sw.define_var("_k",e.first.getMappingTypeName(),e.first.getTypeDefaultValue() )
		sw.define_var('_c1','%shlp'%e.first.name,'new %shlp(_k)'%e.first.name)
		sw.writeln('r = _c1.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_k",e.first.getMappingTypeName(),e.first.getTypeDefaultValue() )
		sw.writeln('r = _k.unmarshall(d);')
		sw.writeln('if(!r) return false;')

	if isinstance(e.second,Builtin):
		sw.define_var("_v",e.second.getMappingTypeName(),e.second.getTypeDefaultValue() )
		Builtin_Python.unserial(e.second.type,'_v','d',sw.idt,sw)
	elif isinstance(e.second,Sequence) or isinstance(e.second,Dictionary):
		sw.define_var("_v",e.second.getMappingTypeName(),e.second.getTypeDefaultValue() )
		sw.define_var('_c2','%shlp'%e.second.name,'new %shlp(_k)'%e.second.name)
		sw.writeln('r = _c2.unmarshall(d);')
		sw.writeln('if(!r) return false;')
	else:
		sw.define_var("_v",e.second.getMappingTypeName(),e.second.getTypeDefaultValue() )
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

	interface_defs[ifidx] = {'e':e,'f':{}}
	sw.classfile_enter(e.getName())
	sw.writeln('import tce.*;')

	#接口对象的委托类
	sw.writeln('import %s.%s_delegate;'%(sw.pkg_current(),e.getName()) )
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
			params.append( (p.id,p.type.getMappingTypeName()) )
		list =[]
		for v,t in params:
			list.append('%s %s'%(t,v))
		s = string.join( list,',')
		if s: s += ','
		sw.writeln('public %s %s(%sRpcContext ctx){'%(m.type.getMappingTypeName(),m.name,s ) ).idt_inc()
		#------------定义默认返回函数----------------------

		if isinstance( m.type ,Builtin ):
			if m.type.name =='void':
#				sw.idt_dec().wln()
				sw.scope_end()
				continue
			else:
				sw.writeln("return %s;"%m.type.getTypeDefaultValue())
		elif isinstance(m.type,Sequence):
			sw.writeln("return %s;"%m.type.getTypeDefaultValue() )
#		elif isinstance(m.type,Dictionary):
#			sw.writeln("return %s;"%m.type.getTypeDefaultValue() )
		else:
			sw.writeln("return %s;"%m.type.getTypeDefaultValue() )
		sw.scope_end()

	sw.scope_end() # end class


	sw.classfile_leave()

#	sw.pkg_end()

	#------- 定义委托对象 ---------------------------
	sw.classfile_enter("%s_delegate"%e.getName())

	sw.writeln("import %s.%s;"%(sw.pkg_current(),e.getName()))
#	sw.writeln("import %s;"%e.getName())
	sw.wln()
	#服务对象调用委托
	sw.writeln("public class %s_delegate extends RpcServantDelegate {"%e.getName()).idt_inc()

	sw.wln()
#	sw.writeln('var index:uint = %s;'%ifidx)
#	sw.writeln('var id:String;')
#	sw.writeln('var adapter:CommAdapter = null;')

#	sw.writeln('public var conn:RpcConnection = null;')
#
	sw.writeln('%s inst = null;'%(e.getName()))

#	sw.wln()
	#构造函数
#	sw.writeln("public %s_delegate(%s inst,adapter:CommAdapter=null,conn:RpcConnection=null){"%(e.getName(),e.getName() )).idt_inc()
	sw.writeln("public %s_delegate(%s inst){"%(e.getName(),e.getName() )).idt_inc()
#	sw.writeln('this.id = ""; ')  #唯一服务类
#	sw.writeln("this.adapter = adapter;")
	sw.writeln('this.index = "%s";'%e.getName() )  #接口的xml名称注册到adapter
#	for opidx,m in enumerate(e.list): # function list
#		sw.writeln("this.optlist.put(%s,this.%s);"%(opidx,m.name)) #直接保存 twoway 和 oneway 函数入口

	sw.writeln("this.inst = inst;")
	sw.scope_end().wln() # finish construct()

	#实现invoke()接口
	sw.writeln("@Override")
	sw.writeln("public boolean invoke(RpcMessage m_){").idt_inc()
#	sw.writeln('boolean r=false;')
	sw.writeln('RpcMessageXML m = (RpcMessageXML)m_;')
	for m in e.list:
		sw.writeln('if(m.msg.equals("%s") ){'%m.name).idt_inc()
		sw.writeln('return %s_delegate(m);'%m.name)
		sw.scope_end()
	sw.writeln('return false;')
	sw.scope_end() # end - invoke()
	sw.wln()

	#开始委托 函数定义
	for opidx,m in enumerate(e.list): # function list
		sw.writeln('public boolean %s_delegate(RpcMessage m_){'%(m.name) ).idt_inc()
		sw.writeln('RpcMessageXML m = (RpcMessageXML)m_;')
		params=[ ]
#		sw.define_var('d','ByteArray')
#		sw.writeln("d = ctx.msg.paramstream; ")
		sw.writeln('boolean r= false;')
		#sw.writeln("idx = 0")
		if m.params:
			sw.writeln('Element node;')
			sw.writeln('NodeList nodes;')
		sw.writeln('r = false;')

		for p in m.params:
			if isinstance(p.type,Builtin):

				sw.writeln('nodes = m.parentNode.getElementsByTagName("%s");'%(p.id) )
			else:
				sw.writeln('nodes = m.parentNode.getElementsByTagName("%s");'%(GrammarXML.extractXMLTag(p.type.name)) )
			if isinstance(p.type,Builtin):
				sw.define_var(p.id,p.type.getMappingTypeName(),p.type.getTypeDefaultValue() )
				sw.writeln('if(nodes.getLength()!=0){').idt_inc()
				sw.writeln('node = (Element)nodes.item(0);')
				Builtin_Python.unserial(p.type,p.id,'node',sw,False)
				sw.scope_end()
			elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):


				sw.define_var(p.id,p.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())

				c = sw.newVariant('_array')
				sw.define_var(c,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
				sw.writeln('if(nodes.getLength()!=0){').idt_inc()
				sw.writeln('node = (Element)nodes.item(0);')
				sw.writeln('r = %s.unmarshall(node,null);'%c)
				sw.writeln('if(!r) return false;')
				sw.scope_end()

			else:
				sw.define_var(p.id,p.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())
				sw.writeln('if(nodes.getLength()!=0){').idt_inc()
				sw.writeln('node = (Element)nodes.item(0);')
				sw.writeln('r = %s.unmarshall(node,null);'%p.id)
				sw.writeln('if(!r) return false;')
				sw.scope_end()

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
			sw.define_var('Result',m.type.getMappingTypeName())
			sw.writeln("Result = servant.%s(%sctx);"%(m.name,ps) )


		sw.writeln("if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){").idt_inc()
		sw.writeln("return true;") #异步调用不返回等待
		sw.scope_end()

		sw.wln()
		#处理返回值
#
#		sw.writeln('d = new ByteArray();')
#		sw.writeln('d.endian = Endian.BIG_ENDIAN;')
		if m.type.name !='void':
			sw.define_var('mr','RpcMessageXML','new RpcMessageXML(RpcMessage.RETURN)')
			sw.writeln('mr.sequence = m.sequence;')
			sw.writeln('mr.msgcls = m.msgcls;')
			sw.writeln('mr.msg = m.msg+"Resp"; ')

	#		sw.writeln("m.sequence = ctx.msg.sequence;") #返回事务号与请求事务号必须一致
	#
			#处理调用返回
			sw.writeln('String xml="";')
			if isinstance( m.type ,Builtin ) and m.type.name!='void':
				Builtin_Python.serial(m.type,'Result',sw,'xml',False)
#				print 'xmlRpc return can not be primitive type:%s'%m.name
#				sys.exit()

			elif isinstance(m.type,Sequence): # or isinstance(m.type,Dictionary):
				v = sw.newVariant('_c')
				sw.define_var(v,'%shlp'%m.type.name,'new %shlp(Result)'%m.type.name)
				sw.writeln('xml = %s.marshall();'%v)
			else:
				sw.writeln("xml = Result.marshall();")


			#sw.writeln("if(d.length) m.addParam(d);")
			sw.writeln('mr.xml = xml;')
			sw.writeln("m.conn.sendMessage(mr);") #发送回去
		sw.writeln("return true;")

		sw.scope_end() # end servant function{}
		sw.wln()
	sw.scope_end() # end class define
	sw.classfile_leave()
#	sw.pkg_end()

	#------------Create Proxy -------------
	#------------Create Proxy -------------
	#------------Create Proxy -------------
	# 创建代理
	sw.classfile_enter('%sProxy'%e.getName())
	sw.wln()

#	sw.writeln('import tce.*;')
	sw.writeln('import java.util.*;')

#	sw.writeln("import %s.%s;"%(sw.pkg_current(), e.getName() ) )
	sw.wln()




	sw.writeln('public class %sProxy extends RpcProxyBase{'%e.getName() ).idt_inc()
	sw.writeln("//# -- INTERFACE PROXY -- ")
#
	sw.wln()
	sw.writeln("%sProxy(RpcConnection conn){"%(e.getName())).idt_inc()
	sw.writeln("this.conn = conn;")
	sw.scope_end().wln()

	#--create()
	sw.writeln('public static %sProxy createWithXML(String host,int port){'%e.getName()).idt_inc()
	sw.writeln('RpcConnection conn = RpcCommunicator.instance().'
			   'createConnection(RpcConsts.CONNECTION_SOCK|RpcConsts.MSG_ENCODE_XML,'
			   'host,port);')
	sw.writeln('%sProxy prx = new %sProxy(conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()

	sw.writeln('public static %sProxy createWithHTTP(String url,String method){'%e.getName()).idt_inc()
#	sw.writeln('RpcConnection conn = RpcCommunicator.instance().'
#			   'createConnection(RpcConsts.CONNECTION_HTTP|RpcConsts.MSG_ENCODE_XML,'
#			   'host,port,method);')
	sw.writeln('RpcConnection conn = new RpcConnection_Http(url,method);')
	sw.writeln('%sProxy prx = new %sProxy(conn);'%(e.name,e.name))
	sw.writeln('return prx;')
	sw.scope_end()
	#-- end create()
	sw.wln()
	#-- begin destroy()
	sw.writeln('public void destroy(){').idt_inc()
	sw.writeln('try{').idt_inc()
	sw.writeln('conn.close();')
	sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
	sw.writeln('RpcCommunicator.instance().getLogger().error(e.getMessage());')
	sw.scope_end()
	sw.scope_end()

	#-- end destroy()


	for opidx,m in enumerate(e.list): # function list
		sw.wln()


		#------------BEGIN TOWAY CALL with timeout ----------------------------------------
		#----------------------------------------------------
		'''
		params=[]
#		interface_defs[ifidx]['f'][opidx] = m	#记录接口的函数对象
		list =[]
		for p in m.params:
#			params.append( p.id,p.type.getMappingTypeName())
			list.append('%s %s'%(p.type.getMappingTypeName(),p.id) )
		s = string.join( list,',')
		# 函数定义开始
		if s: s = s + ','

		#-- 生成同步函数
		sw.writeln('// timeout - msec ,  0 means waiting infinitely')
		sw.writeln('public %s %s(%sint timeout) throws RpcException{'%(m.type.name,m.name,s) ).idt_inc()
#		sw.writeln("//# function index: %s"%idx).wln()
		sw.define_var('r','boolean','false')
#		sw.writeln("try{").idt_inc()
#		sw.define_var('ecode','int','tcelib.RpcConsts.RPCERROR_SUCC')
#		sw.writeln("ecode = tcelib.RpcConsts.RPCERROR_SUCC;")
		sw.define_var('m','RpcMessageXML','new RpcMessageXML(RpcMessage.CALL)')
		sw.writeln('m.msgcls ="%s";'%e.name)
		sw.writeln('m.msg = "%s";'%m.name)
#		sw.writeln("m.ifidx = %s;"%ifidx)
#		sw.writeln("m.opidx = %s;"%opidx)

#		sw.define_var('d','ByteArray')
#		sw.define_var('_h','HashMap','new HashMap()')
		for p in m.params:
#			sw.writeln('d = new ByteArray();')
			if isinstance(p.type,Builtin):
				print 'fucntion param can not be primitive type:%s '%(m.name,p.type.name)
				sys.exit()
#				Builtin_Python.serial(p.type.type,p.id,idt,sw)
			elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
				v = sw.newVariant('_c')
#				sw.writeln('_ar = new ByteArray();')
				sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
				sw.writeln('m.xml+=%s.marshall();'%v)
#			elif isinstance(p.type,Dictionary):
#				v = sw.newVariant('_c')
##				sw.writeln('_h = new HashMap();')
#				sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
#				sw.writeln('%s.marshall(d);'%v)
			else:
				sw.writeln("m.xml+=%s.marshall();"%p.id)
		# 完成参数打包
#			sw.writeln("m.addParam(d);")
		sw.writeln("m.prx = this;")
#		sw.writeln("m.async = async;")
#		sw.writeln("m.asyncparser = this.%s_asyncparser as Function;"%(m.name ) )
		sw.writeln("r = this.conn.sendMessage(m);")
		sw.writeln("if(!r){").idt_inc()
#		sw.writeln("ecode = tcelib.RpcConsts.RPCERROR_SENDFAILED;")
#		sw.writeln("return ecode;")
		sw.writeln('throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);')
		sw.scope_end() # end if()

#		sw.writeln("if(async == null){").idt_inc()
#		sw.writeln("return tcelib.RpcConsts.RPCERROR_SUCC;")
#		sw.scope_end()

#		sw.idt_dec()
#		sw.writeln("}catch(RpcException e){").idt_inc()
#		sw.writeln("return tcelib.RpcConsts.RPCERROR_DATADIRTY;")
#		sw.scope_end()
#
# 		sw.writeln("return tcelib.RpcConsts.RPCERROR_SUCC;")
		#BEGIN WAITING
		sw.writeln('try{').idt_inc()
		sw.writeln('synchronized(m){').idt_inc()
		sw.writeln('if( timeout > 0) m.wait(timeout);')
		sw.writeln('else m.wait();')
		sw.scope_end() # end synchronized()
		sw.idt_dec().writeln('}catch(Exception e){').idt_inc()
		sw.writeln('throw new RpcException(RpcConsts.RPCERROR_INTERNAL_EXCEPTION,e.getMessage());')
		sw.scope_end()

		#检测错误码
		sw.writeln('if (m.errcode != RpcConsts.RPCERROR_SUCC){').idt_inc()
		sw.writeln('throw new RpcException(m.errcode);')
		sw.scope_end()

		sw.writeln('if( m.result == null){').idt_inc() #网络断开
		sw.writeln('throw new RpcException(RpcConsts.RPCERROR_TIMEOUT);') #超时
		sw.scope_end()

		if m.type.name !='void':
			sw.writeln('RpcMessageXML m2 = (RpcMessageXML) m.result;')

	#		sw.writeln('try{').idt_inc()
			v = sw.newVariant('_b')
			sw.define_var(v,m.type.name,m.type.getTypeDefaultValue() )
			#返回值必须是 sequence 或者 struct
			if  isinstance(m.type,Sequence):
				c = sw.newVariant('_array')
				sw.define_var(c,'%shlp'%m.type.name,'new %shlp(%s)'%(m.type.name,v))
				sw.writeln('r = %s.unmarshall(null,m2.parentNode);'%c)

			elif isinstance(m.type,Struct):
				sw.writeln('r = %s.unmarshall(null,m2.parentNode);'%v)
			else:
				if m.type.name !='void':
					print 'proxy call return value is invalid: %s %s()'%(m.type.name,m.name)
					sys.exit()

			#shit  返回的xml数据可能不完整，必须允许这种方式
#			sw.writeln('if(!r){').idt_inc()
#			sw.writeln('throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);')
#			sw.scope_end()

			sw.writeln('return %s; //regardless if  unmarshalling is okay '%v)




		sw.scope_end() # end function()
		#end rpc proxy::call()  --

		sw.wln()
		'''

		#---------- BEGIN ONEWAY CALL ------------------------------------------
		#-----------Just  void return  ONEWAY call -----------------------------------------
		if m.type.name =='void':
			params=[]
			list =[]
			for p in m.params:
				list.append('%s %s'%(p.type.getMappingTypeName(),p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s

#			sw.writeln('public %s %s_oneway(%s) throws RpcException{'%(m.type.name,m.name,s) ).idt_inc()
			sw.writeln('public %s %s_oneway(%s,HashMap<String,String> head){'%(m.type.name,m.name,s) ).idt_inc()
			sw.define_var('r','boolean','false')

			sw.define_var('m','RpcMessageXML')
			sw.writeln("if(this.conn.getType() == RpcConsts.CONNECTION_HTTP){").idt_inc()
			sw.writeln('m =new RpcMessageHttp(RpcMessage.CALL);')
			sw.idt_dec().writeln('}else{').idt_inc()
			sw.writeln('m =new RpcMessageXML(RpcMessage.CALL|RpcMessage.ONEWAY);')
			sw.scope_end()

			sw.writeln('m.msgcls = "%s";'%e.name)
			sw.writeln('m.msg = "%s";'% m.name)
			sw.writeln('m.conn = this.conn;')
			for p in m.params:
				if isinstance(p.type,Builtin):
#					print 'fucntion param can not be primitive type:%s '%(m.name,p.type.name)
#					sys.exit()
					Builtin_Python.serial(m.type,p.id,sw,'m.xml',False)
				elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
					v = sw.newVariant('_c')
					sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
					sw.writeln('m.xml+=%s.marshall();'%v)
				else:
					sw.writeln("if(this.conn.getType() == RpcConsts.CONNECTION_HTTP){").idt_inc()
					sw.writeln("m.xml+=%s.marshall_http_get();"%p.id)
					sw.writeln("m.http_params = %s.http_params;"%p.id)
					sw.writeln('}else{').idt_inc()
					sw.writeln("m.xml+=%s.marshall();"%p.id)
					sw.scope_end()

			sw.writeln("m.prx = this;")
			sw.writeln("m.http_head = head;")
			sw.writeln('RpcMessageAsyncDispatcher.instance().sendMessage(m);')
#			sw.writeln("r = this.conn.sendMessage(m);")
#			sw.writeln("if(!r){").idt_inc()
#			sw.writeln('throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);')
#			sw.scope_end() # end if()
			sw.scope_end() # end function()
			#end rpc proxy::call()  --

			sw.wln()

		#---------- END ONEWAY CALL ------------------------------------------

		#---------- BEGIN ASYNC CALL ------------------------------------------
		#-----------  void return not be supported -----------------------------------------
		if m.type.name !='void':
			params=[]
			list =[]
			for p in m.params:
				list.append('%s %s'%(p.type.getMappingTypeName(),p.id) )
			s = string.join( list,',')
			# 函数定义开始
			if s: s = s + ','

#			s_AsyncCallBack

#			sw.writeln('public void %s_async(%s%s_AsyncCallBack async) throws RpcException{'%(m.name,s,e.name) ).idt_inc()
			sw.writeln('public void %s_async(%s%s_AsyncCallBack async,HashMap<String,String> head) {'%(m.name,s,e.name) ).idt_inc()
			sw.define_var('r','boolean','false')

			sw.define_var('m','RpcMessageXML')
			sw.writeln("if(this.conn.getType() == RpcConsts.CONNECTION_HTTP){").idt_inc()
			sw.writeln('m =new RpcMessageHttp(RpcMessage.CALL);')
			sw.idt_dec().writeln('}else{').idt_inc()
			sw.writeln('m =new RpcMessageXML(RpcMessage.CALL|RpcMessage.ONEWAY);')
			sw.scope_end()

#			sw.define_var('m','RpcMessageXML','new RpcMessageXML(RpcMessage.CALL|RpcMessage.ASYNC)')
#			sw.writeln('m.opname="%s";'%)
			sw.writeln('m.msgcls ="%s";'% e.name)
			sw.writeln('m.msg = "%s";'%m.name)
			sw.writeln('m.conn = this.conn;')
			for p in m.params:
				if isinstance(p.type,Builtin):
#					print 'fucntion param can not be primitive type:%s '%(m.name,p.type.name)
#					sys.exit()
					Builtin_Python.serial(m.type,p.id,sw,'m.xml',False)
				elif isinstance(p.type,Sequence): # or isinstance(p.type,Dictionary):
					v = sw.newVariant('_c')
					sw.define_var(v,'%shlp'%p.type.name,'new %shlp(%s)'%(p.type.name,p.id))
					sw.writeln('m.xml+=%s.marshall();'%v)
				else:
#					sw.writeln("m.xml+=%s.marshall();"%p.id)
					sw.writeln("if(this.conn.getType() == RpcConsts.CONNECTION_HTTP){").idt_inc()
					sw.writeln("m.xml+=%s.marshall_http_get();"%p.id)
					sw.writeln("m.http_params = %s.http_params;"%p.id)
					sw.writeln('}else{').idt_inc()
					sw.writeln("m.xml+=%s.marshall();"%p.id)
					sw.scope_end()


			sw.writeln("m.prx = this;")
			sw.writeln('m.async = async;')
			sw.writeln("m.http_head = head;")
			sw.writeln('RpcMessageAsyncDispatcher.instance().sendMessage(m);')
#			sw.writeln("r = this.conn.sendMessage(m);")
#			sw.writeln("if(!r){").idt_inc()
#			sw.writeln('throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);')
#			sw.scope_end() # end if()
			sw.scope_end() # end function()
			#end rpc proxy::call()  --

			sw.wln()

		#---------- END ASYNC CALL ------------------------------------------
		sw.wln()
	sw.scope_end() # end class  '}'
	sw.classfile_leave()

	#---------------异步调用 --------------------

	sw.classfile_enter('%s_AsyncCallBack'%(e.getName()))
	sw.wln()

	sw.writeln('public class %s_AsyncCallBack extends RpcAsyncCallBackBase{'%(e.getName() )).idt_inc()
	#定义异步回调接收函数

	sw.writeln('// following functions should be ovrrided in user space.')
	for m in e.list: # func
		if m.type.name =='void': continue
		sw.writeln('public void %s(%s result,RpcProxyBase proxy){'%(m.name,m.type.getMappingTypeName() )).idt_inc()
		sw.scope_end()
		sw.wln()

	sw.writeln('protected void onError(String callname,String errmsg,RpcProxyBase proxy){').idt_inc()

	sw.scope_end().wln()


#	sw.writeln('@Override')
	sw.writeln('public final void callReturn(RpcMessage m1_,RpcMessage m2_){').idt_inc()
	sw.writeln('NodeList nodes;')
	sw.writeln('Element node;')
	sw.writeln('boolean r = false;')
	sw.writeln('RpcMessageXML m1 = (RpcMessageXML)m1_;')
	sw.writeln('RpcMessageXML m2 = (RpcMessageXML)m2_;')
	sw.writeln('if(m1 == m2){').idt_inc() #错误码
	sw.writeln('onError(m1.msg ,RpcConsts.ErrorString(m1.errcode),m1.prx );')
	sw.writeln('return;')
	sw.scope_end() # error_callback()

	cnt = 0
	for m in e.list:
		if m.type.name == 'void': continue
#		print m.type.name
#		if not cnt:
		sw.writeln('if(m1.msg == "%s"){'%m.name).idt_inc()

		if isinstance(m.type,Builtin): #返回值都用 <Result></Result>
			sw.writeln('nodes = m2.parentNode.getElementsByTagName("%s");'%('Result') )
		else:
			sw.writeln('nodes = m2.parentNode.getElementsByTagName("%s");'%(GrammarXML.extractXMLTag(m.type.name)) )
		cnt+=1
		sw.writeln('if(nodes.getLength() !=0) {').idt_inc()
		if isinstance(m.type,Builtin):
			sw.define_var('Result',m.type.getMappingTypeName(),m.type.getTypeDefaultValue() )

			sw.writeln('node = (Element)nodes.item(0);')
			Builtin_Python.unserial(m.type,'Result','node',sw,False)

		elif isinstance(m.type,Sequence): # or isinstance(p.type,Dictionary):
			v = sw.newVariant('_b')
			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%p.type.getMappingTypeName())

			c = sw.newVariant('_array')
			sw.define_var(c,'%shlp'%m.type.name,'new %shlp(%s)'%(m.type.name,v))
#			sw.writeln('if(nodes.getLength()!=0){').idt_inc()
			sw.writeln('node = (Element)nodes.item(0);')
			sw.writeln('r = %s.unmarshall(node,null);'%c)
#			sw.writeln('if(r) %s(%s,%s);'%(m.name,v,'m1.prx'))
			sw.writeln('%s(%s,%s);'%(m.name,v,'m1.prx')) # 不考虑unmarshall()是否okay

#			sw.scope_end()

		else:
			v = sw.newVariant('_b')
			sw.define_var(v,m.type.getMappingTypeName(),'new %s()'%m.type.getMappingTypeName())
#			sw.writeln('if(nodes.getLength()!=0){').idt_inc()
			sw.writeln('node = (Element)nodes.item(0);')
			sw.writeln('r = %s.unmarshall(node,null);'%v)
#			sw.writeln('if(r) %s(%s,%s);'%(m.name,v,'m1.prx'))
			sw.writeln('%s(%s,%s);'%(m.name,v,'m1.prx')) #不考虑unmarshall是否okay

#			sw.scope_end()
		sw.writeln('return ;')
		sw.scope_end() # enf if length != 0

		sw.scope_end()

	sw.scope_end() # end funcion callReturn()

	sw.scope_end() # end class  '}'
	sw.classfile_leave()


	return


def createCodeInterfaceMapping():
	global interface_defs # {e,f:{}}
	pass




def createCodeFrame(e,idx,sw ):
	idt = Indent()

	txt='''
import tce.*;
//import javax.xml.parsers.*;
import org.w3c.dom.*;
//import java.io.*;
//import java.util.*;
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
#		sw.classfile_enter(e.getName(),'%shlp'%e.getName())
#		createCodeDictionary(e,sw,idt)
#		sw.classfile_leave()
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
	file = ''

	ostream = Outputer()
	#ostream.addHandler(sys.stdout)

	argv = sys.argv
	outdir ='.'
	pkgname = ''
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

		if p == '-pkg':
			if argv:
				pkgname = argv.pop(0)

	fp = open(file,'r')
	content = fp.read()
	fp.close()

#	print outdir
	os.chdir( outdir )
	sw = StreamWriter()
	name = os.path.basename(file).split('.')[0]
	if not pkgname:
		pkgname = name
#	print pkgname
	sw.createPackage(pkgname)
	sw.pkg_enter(pkgname)


#	ostream.write(headtitles)
	unit = syntax_result(content)
	for idx,e in enumerate(unit.list):
		createCodeFrame(e,idx,sw)
		ostream.write(NEWLINE)

	sw.pkg_leave()





lexparser.language = 'java'

if __name__ =='__main__':
	createCodes()


# usage:
# 	tce2java_xml.py
# 			-i /Users/socketref/Desktop/projects/dvr/ply/code/java/test/sns_mobile_xml.idl
# 				-o /Users/socketref/Desktop/projects/dvr/ply/code/java


#	a=[10,20]
#	t = TA(a)
#	t.test()
#	print a


