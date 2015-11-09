#--coding:utf-8--


#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#

import	sys



if	".."	not	in	sys.path:	sys.path.insert(0,"..")

import os,sys,os.path,struct,time,traceback,string

import	ply.lex	as	lex
import ply.yacc as yacc

from lexparser import *
import lexparser
import lexparser as myparser

'''
默认是SLR，我们也可以通过参数指定为 LALR(

idl
interface定义 函数参数保留名称： d,idx,m

2013.9.8
  1.相同module名的接口可以被定义在不同idl文件
'''


#本地module内数据类型
# local_types_def={}
# local_ifs_def={} #本地接口数组

local_ifs_def_stack=[]
local_types_def_stack=[]

imported_files=[]


def getTypeDef(type):
	#本地module，声明不带::
	# print local_types_def_stack
	types = local_types_def_stack[-1]
#	print types
	t = types.get(type,None)
	if not t:
		t = global_types_defs.get(type,None)
	return t

def getInterfaceDef(name):
	types = local_types_def_stack[-1]
#	print name ,types
	ifx = types.get(name,None)
	if not ifx:
		ifx = global_types_defs.get(name,None)
	return ifx


tokens=(
		'IDENTIFIER','STRUCT','NUMBER','INTERFACE',
		'SEQUENCE','DICTIONARY','EXCEPTION','COMMENTLINE',
		'IMPORT','MODULE','NAMESPACEIDENTIFIER','EXTENDS',
		'FILENAME'
#		'VOID',
	)

def t_COMMENTLINE(t):
	'//.*\n'

def t_SEQUENCE(t):
	'sequence'
	return t

def t_DICTIONARY(t):
	'dictionary'
	return t


def t_STRUCT(t):
	'struct'
	return t


def t_INTERFACE(t):
	'interface'
	return t

def t_IMPORT(t):
	'import'
	return t

def t_EXTENDS(t):
	'extends'
	return t

#def t_VOID(t):
#	'void'
#	return t

def t_MODULE(t):
	'module'
	return t



def t_FILENAME(t):
	'''
		[A-Za-z0-9_]*\.+[A-Za-z0-9_]*
	'''
#	'''[A-Za-z0-9_\.]+'''
	#'''\"[A-Za-z0-9_\.]+\"'''
	return t

def t_IDENTIFIER(t):
	'[A-Za-z_][A-Za-z0-9_]*'
	return t

def t_NAMESPACEIDENTIFIER(t):
	'[A-Za-z_][A-Za-z0-9_]*\:\:[A-Za-z_][A-Za-z0-9_]*'
	return t

t_NUMBER=r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

t_ignore	=" 	\t"

def	t_newline(t):
	r'\n'
	t.lexer.lineno	+=	1 #int(t.value) #.count("\n")


def	t_error(t):
#	print t
	print("Illegal	character	'%s'"	%	t.value[0])
	t.lexer.skip(1)

literals = [ '{','}',';','(',')','<','>',',' ,':','"']

#	Build	the	lexer
lexer = lex.lex()

#literals = [ ':',',','(',')' ]



#lexer.input(data)

#while 1:
#	tok = lexer.token()
#	if not tok: break	
	#print tok.type,tok.value
#sys.exit()


def p_start(t):
	'''start : doc_elements
		|
	'''
#	print '-'*20,len(t)
	unit = Unit()
#	unit.addChild(t[1])
	t[0] = unit

def p_doc_elements(t):
	'''
		doc_elements : doc_element
	'''
	t[0] = [t[1],]

def p_doc_elements_2(t):
	'''
		doc_elements : doc_elements doc_element
	'''
	if type(t[1]) != type([]):
		t[0] = [t[2],t[1]]
	else:
		t[1].append(t[2])
		t[0] = t[1]

def p_doc_element(t):
	'''
		doc_element : module_def
			| import
	'''


def p_include(t):
	'''
		import : IMPORT  IDENTIFIER
	'''
	# global curr_idl_path

	t[0] = t[2]

	filename = t[2].strip()
	if imported_files.count(filename):
		return
	imported_files.append(filename)



	print '>> process import file:',t[2]
	lexer  = lex.lex()       # Return lexer object
	parser = yacc.yacc()
	# print lexparser.curr_idl_path
	idl = os.path.join(lexparser.curr_idl_path, t[2]+".idl")
	try:
		text = open(idl,'r').read()
	except:
		print 'IDL file access: <%s> denied!'%idl
		sys.exit()

	local_ifs_def_stack.append({})
	local_types_def_stack.append({})
	parser.parse(text,lexer=lexer)

	local_ifs_def_stack.pop()
	local_types_def_stack.pop()

def p_module_def(t):
	'''module_def : MODULE IDENTIFIER '{' module_elements '}'   '''
	id = t[2]

	m = getModuleDef(id)
	if not m:
		m = Module(id)
		global_modules_defs[id] = m
		global_modules.append(m)

	# print 'module:',id,'contains:',t[4]

	for e in t[4]:
		if e == None:
			continue
		e.container = m
		e.module = id #设置关联
		# print 'element %s in module:%s'%(e.name,id)
		if m.children.get(e.name):
			print 'element : ',e.name, ' has been declared in module:',id
			sys.exit()

		m.children[e.name] = e
		m.list.append(e)

		global_types_defs['%s::%s'%(id,e.name)] = e
#		types = local_types_def_stack[-1]
#		types[e.name] = e

	t[0] = m
#	print 'global_types_defs:',global_types_defs.keys()
#	print 'global_ifs_defs:',global_ifs_defs.keys()
	return

#	st  = Struct(id)
#	print t[4]
#	t[4].reverse()
#	for dm in t[4]:
#		if not st.createDataMember(dm):
#			print 'error: datamember<%s> name<%s> has existed!'%(id,dm.id)
#			sys.exit()
#
#	types_def[id] = st	#注册数据类型到全局类型表


def p_module_elements(t):
	'''
		module_elements : module_element_def
	'''
	t[0] = [t[1],]
#	print dir(t[0])
#	print t[1]
#	print repr(t[0])

def p_module_elements_2(t):
	'''
		module_elements :  module_elements module_element_def
	'''
	if type(t[1]) != type([]):
		t[0] = [t[2],t[1]]
	else:
		t[1].append(t[2])
		t[0] = t[1]

#	if type(t[2]) != type([]):
#		t[0] = [t[1],t[2]]
#	else:
#		t[2].append(t[1])
#		t[0] = t[2]
#	print t[0]

def p_module_element_def(t):
	''' module_element_def :  struct_def ';'
			| interface_def ';'
			| sequence_def ';'
			| dictionary_def ';'
			|
	'''
	if len(t) > 1:
		t[0]=t[1]
		# print t[1].name,t[1]
	else:
		t[0] = None
	# local_types_def[t[1].name] = t[1]



def p_sequence_def(t):
	'''
		sequence_def : SEQUENCE '<' type '>' IDENTIFIER
	'''

	name = t[5]

	if not checkVariantName(name,False):
		print 'error: sequence<%s>.%s illegal!'%(t[3],name)
		sys.exit()

#	if getTypeDef(name):
#		print 'error: line %s sequence (%s) has existed!'%(t.lineno(1),name)
#		sys.exit() #sequence的类型名存在

	type_ = t[3]

	seq = Sequence(name,type_)


	types = local_types_def_stack[-1]
	types[name] = seq

	t[0] = seq

def p_dictionary_def(t):
	'''
		dictionary_def : DICTIONARY '<' type ',' type '>' IDENTIFIER
	'''
	first = t[3]
	second = t[5]
	name = t[7]
#	print first,second,name

	if not checkVariantName(name,False):
		print 'error: dictionary < %s > illegal!'%(name)
		sys.exit()

#	if getTypeDef(name):
#		print 'error: line %s dictionary type (%s) has existed!'%(t.lineno(1),name)
#		sys.exit() #sequence的类型名存在
#


	dict = Dictionary(name,first,second)

#	types = local_types_def_stack[-1]
#	types[name] = dict
	t[0] = dict

def p_interface_def(t):
	'''
		interface_def :  INTERFACE IDENTIFIER '{' operatemembers '}'
			| INTERFACE IDENTIFIER EXTENDS type '{' operatemembers '}'
	'''
#	print t[1],t[2]
	id = t[2]
#	ifx = getInterfaceDef(id)
#	if ifx:
#		print 'error: interface name(%s) has existed!'%id
#		sys.exit()


	ifc = Interface(id)
	if len(t) == 8:
		superif =  t[4]
#		print 'super if:',superif.name
#
#		if not getInterfaceDef(superif.name):
#			print 'error(p_interface_def): specified interface:< %s > not defined!'%superif
#			sys.exit()
		ifc.superif = superif

		opms = t[6]
	else:
		opms = t[4]
#	opms.reverse()
	#检测函数名称是否有重复
#	print opms
	ifc.opms = opms

#	for opm in opms:
#		if not ifc.createOperateMember(opm,id,t):
#			print 'error(p_interface_def): line %s createOperateMember failed! interface:: %s.%s'%( t.lineno(3),t[2],opm.name)
#			sys.exit()
#
#
#	types = local_types_def_stack[-1]
#	types[id] = ifc

	t[0] = ifc # reduce to syntax tree  ...



def p_operatemembers(t):
	'''
		operatemembers : operatemember
	'''
	#print 'operatemember num:',len(t) # 1 means no operatemebmer
#	if len(t) > 1:
#		t[0] = t[1]
#	else:
#		t[0] = []
	t[0] = [t[1],]


def p_operatemembers_2(t):
	'''
		operatemembers :  operatemembers operatemember
	'''
	if type(t[1]) != type([]):
		t[0] = [t[2],t[1]]
	else:
		t[1].append(t[2])
		t[0] = t[1]

def p_operatemember(t):
	'''
		operatemember : callreturn IDENTIFIER '(' operateparams ')' ';'

	'''
	params = t[4]
	params.reverse()	# 这里必须进行倒置一下

	# 2013.5.30  参数都添加 '_' 后缀
#	for p in params:
#		p.id+='_'

	opm = OperateMember(t[2],t[1],params)
	t[0] = opm
#	print 'x1.',opm

def p_operateparams(t):
	'''
		operateparams : type_id
			|
	'''
	if len(t) > 1:
		t[0] = [ t[1],]
	else:
		t[0] =[ ]


def p_operateparams_2(t):
	'''
		operateparams : type_id ',' operateparams
	'''

	t[3].append(t[1])
	t[0] = t[3]

def p_callreturn(t):
	'''
		callreturn : type
	'''
	t[0] = t[1]


def p_struct_def(t):
	''' struct_def : STRUCT IDENTIFIER '{' datamembers '}' '''
	id = t[2]
	if not checkVariantName(id):
		print 'struct id: %s invalid!'%id
		sys.exit()

#	type = getTypeDef(id)
#	if  type:
#		print 'error struct name:%s existed!'%(id)
#		sys.exit()

	st  = Struct(id)
#	print t[4]
	if not t[4]:
		print 'error: struct <%s> cannot be empty!'%id
		sys.exit()
#	t[4].reverse()
	for dm in t[4]:
		if not st.createDataMember(dm):
			print 'error: datamember<%s> name<%s> has existed!'%(id,dm.id)
			sys.exit()

#	types_def[id] = st	#注册数据类型到全局类型表
	#print types_def
#	types = local_types_def_stack[-1]
#	types[id] = st

	t[0] = st



def p_datamembers(t):
	'''
	datamembers :  datamember 
	'''
	#print t[1]
	#t[0] = t[1]
	t[0] = [t[1],]
	#print 'a1..'
	#print t[0]

def p_datamembers_2(t):
	'''
	datamembers : datamembers datamember
	'''
	if type(t[1]) != type([]):
		t[0] = [t[2],t[1]]
	else:
		t[1].append(t[2])
		t[0] = t[1]


def p_datamember(t):
	'''
	datamember : type_id ';'
	'''
	#print 'datamenber..'
	t[0] =  t[1]

def p_type_id(t):
	'''
		type_id : type IDENTIFIER
	'''
	#print t[1],t[2]
	id = t[2]
	keys = kwds
	# if lexparser.language == 'py':
		#keys +=['def','import','from','type','str','int','float','class']
	keys += lexparser.lang_kws
	if keys.count(id):
		t[2] = t[2] + '_'
	# if not checkVariantName(id):
	# 	print 'error: type_id.id<%s> illegal!'%(id)
	# 	sys.exit()

	t[0] = TypeId(t[1],t[2])




def p_type(t):
	'''type : IDENTIFIER
		| IDENTIFIER ':' ':' IDENTIFIER
	'''
	id = t[1]
	if len(t) == 5:
		id = '%s::%s'%(t[1],t[4])
	# print id
#	type = getTypeDef(t[1])
#	print id
	t[0] = id
#	type = getTypeDef(id)
#
#	if type:
#		t[0] = type
#	else:
#		print 'error(p_type): line %s'%(t.lineno),' type:%s not defined!'%id
#		sys.exit()


def p_error(t):
	print repr(t), t.value,t.type
	print("Syntax error at '%s'" % t)
	#print t.lineno,t.lexpos
	sys.exit()

yacc.yacc(debug=True,method="SLR")

data='''

sequence < int > IntList;

struct student { 
	int x;
	int y;
	int z;
	double fractor;
	IntList ids;
};

interface booksystem{
	int test1(int age);
	int test2(int age);
};

struct dog{
	int name;
	string dog;
	int name2;
	student st1;
};



'''

data='''

struct animal{
	int x;
};

sequence < animal > IntList;

struct student {
	int x;
	int y;
	int z;
	double fractor;
	IntList ids;
};

interface booksystem{
	int test1(int age);
	int test2(int age);
};

sequence<IntList>  XX;
dictionary<int,int> int2_t;
dictionary<int2_t,string> intstr_t;

'''

def filterComments(data):
	return data
	lines = data.split("\n")
	result=[]
	for line in lines:
		x = line.strip()
		if x and x[0] =='#':
			continue
		result.append(line)
	data = string.join(result,'\n')
	return data

def module_type_parse(typename,n,m):


	t = types_def.get(typename) # builtin types check
	if not t:
#		t = m.children.get(typename) #本module中不存在数据类型
		for p in range(n):
			if typename == m.list[p].name:
				t = m.list[p]
				break

		if not t:
			print '>>',typename
			# print '.'*20 ,typename.name
			# print global_modules_defs['sns'].children
			ns = typename.split('::')
			ns = map(string.strip,ns)
			if len(ns) > 1:
				ref_m = global_modules_defs.get(ns[0]) # B::Box
				# print global_modules_defs,ns[0]
				if ref_m:
					print ref_m.children
					t = ref_m.children.get(ns[1])
					if t:
						m.ref_modules[ns[0]]='' #引用到ns[0]模块,用于生成 #include <ref_module>
						# print 'module <%s> references:'%m.name,m.ref_modules
	return t

def parse_idlfile(idlfile):
	import os.path
	#防止重复解析
	# filename = idlfile.split('.')[0]
	filename = os.path.splitext(idlfile)[0] # 2015.11.9 scott
	filename = os.path.basename(filename)  # 2015.11.9 scott
	if imported_files.count(filename):
		return
	imported_files.append(filename)



	lexer  = lex.lex()       # Return lexer object
	parser = yacc.yacc()
	idl = os.path.join(idlfile)
	try:
		text = open(idl,'r').read()
		text.replace('\r','\n\r')
		text = filterComments(text)

		local_ifs_def_stack.append({})
		local_types_def_stack.append({})
		parser.parse(text,lexer=lexer)
		local_ifs_def_stack.pop()
		local_types_def_stack.pop()


	except:
		print 'IDL file access: <%s> denied!'%idl
		traceback.print_exc()
		sys.exit()




def syntax_result(data=''):
	# local_types_def={}
	# local_ifs_def={}

	#开始解析，退入堆栈


	local_ifs_def_stack.append({})
	local_types_def_stack.append({})

	if data:
		r = yacc.parse( filterComments(data))



#	print global_types_defs.keys()
	# for name,m in global_modules_defs.items():
	for m in global_modules:
		name = m.name
		# print 'module :', name,m.children.keys()
		for n in range(len(m.list)):
			e = m.list[n]
			#-- sequence array
			if isinstance(e,Sequence):
				t = module_type_parse(e.type,n,m)
				if not t:
					print 'data type : <%s> unreferenced by Sequence: <%s> ,in module:<%s>'%(e.type,e.name,m.name)
					sys.exit()
				e.type = t #
				# print t,t.name
			#--dictionary hash
			if isinstance(e,Dictionary):
				t = module_type_parse(e.first,n,m)
				if not t:
					print 'error: data type<KEY> : <%s> unreferenced in Dictionary: <%s> ,in module:<%s>'%(e.first,e.name,m.name)
					sys.exit()
				e.first = t
				t = module_type_parse(e.second,n,m)
				if not t:
					print 'error: data type<VALUE> : <%s> unreferenced in Dictionary: <%s> ,in module:<%s>'%(e.second,e.name,m.name)
					sys.exit()
				e.second = t
				# print 'dictionary:',e.name,' key:',e.first.name,' value:',e.second.name
			#-- struct
			if isinstance(e,Struct):
#				if m.children.keys().count(e.name) >1:
#					print 'error: multipule vairaint:%s be defined!'%e.name
#					sys.exit()
				for dm in e.list:
					id,type = dm.name,dm.type # TYPE id;
					# print 'struct member: %s > %s'%(type,id)
					#检查 struct的member类型名称是否被定义

					t = module_type_parse(type,n,m)
					# print t,type,types_def
					if not t:
						print 'error: data type = <%s> undefined in Struct: <%s> ,in module:<%s>'%(type,e.name,m.name)
						sys.exit()
					dm.type = t

			#-- interface --
			if isinstance(e,Interface):
				#处理基类接口 chained to super interface
				if e.superif: #super class type is str
					t = module_type_parse(e.superif,n,m)
					#  t - base interface
					if not t or  not isinstance(t,Interface):
						print 'error: base interface name:<%s> invalid in interface decalaration. '%(e.superif)
						sys.exit()
					print 'super interface:<%s> in interface <%s>'%(t.name,e.name)
					e.superif = t
				for opm in e.opms:
					# print  'interface:<%s> return:<%s> function:<%s> '%(e.name,opm.type,opm.name)
					#--检测参数名称是否重复
					params = map(lambda p:p.id,opm.params)
					for p in opm.params: # p - TypeId
						if params.count(p.id) > 1:
							print 'error: function param: <%s> duplicated in function %s of interface %s'%(p.id,opm.name,e.name)
							sys.exit()
						# print  '>> interface:%s function:%s param:%s %s'%(e.name,opm.name, p.type,p.id)
						#-- 检测参数类型是否合法
						t = module_type_parse(p.type,len(m.list),m)
						if not t:
							print 'error: param <%s:%s> of function <%s> of interface <%s> invalid!'%(p.type,p.id,
							                                                                     opm.name,e.name)
							sys.exit()
						p.type = t
					# 检测函数返回值类型是否合法
					t = module_type_parse(opm.type,len(m.list),m)
					if not t:
						print 'error: return Type <%s> of function <%s> of interface <%s> invalid!'%(p.type,opm.name,e.name)
						sys.exit()
					opm.type = t
					e.createOperateMember(opm)

	# print global_modules_defs

data='''

//import test

module Test{

struct Animal{
	int x;
//	Graphic g;
};

dictionary<string,int> StrInt;

sequence < Animal > IntList;

//interface Parts extends base::DisplayEnd{
interface Parts {
	void booking();
};

interface Engine extends Parts{
	//void start(base::Box box);
	//void booking();
	void no1();
	int named(string name,float degree);
};

//interface ExternCls extends base::DisplayEnd{
//	void navigate(Test::Graphic g,base::Box box);
//};

}

module Second{
	struct People{
		int many;
		//IntList ids;
		Test::Animal animal;
	};
}


'''
if __name__=='__main__':
	syntax_result(data)

#	print global_types_defs.keys()
#	print global_modules_defs.keys()
	#打印接口函数列表
#	for name,ifx in global_ifs_defs.items():
#		print 'interface:',name,' members:',ifx.getOperateNames()




