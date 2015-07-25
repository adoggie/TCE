#--coding:utf-8--

import os,os.path,sys,struct,time,traceback,time
sys.path.insert(0,'../../../../python')
import tcelib as tce
from test import *


class TerminalImpl(ITerminal):
	def __init__(self):
		ITerminal.__init__(self)

	def onMessage(self,message,ctx):
		print 'onMessage:',message

def call_twoway():
		print prx.echo("hello")


def call_timeout():
	try:
		print prx.timeout(3,6)
	except tce.RpcException, e:
		print e.what()


def call_async():

	def hello_callback_async(result,proxy,cookie):
		print 'async call result:',result
		print 'cookie:',cookie

	prx.echo_async('pingpang',hello_callback_async,'it is cookie')


#传递附加数据
def call_extras():
	print prx.echo("hello",extra={'name':'scott.bo'})


def call_oneway():
	prx.heartbeat_oneway('hello world!')


def call_bidirection():
	adapter = tce.RpcCommAdapter('adapter')
	impl = TerminalImpl()
	adapter.addConnection(prx.conn)
	adapter.addServant(impl)
	tce.RpcCommunicator.instance().addAdapter(adapter)

	prx.bidirection_oneway()


def Proxy():
	"""
	获得常规socket代理
	:return:
	"""
	ep = tce.RpcEndPoint(host='localhost',port=16005)
	return  ServerPrx.create(ep)

def sslProxy():
	ep = tce.RpcEndPoint(host='localhost',port=16005,ssl=True)
	return ServerPrx.create(ep)

tce.RpcCommunicator.instance().init()
# prx = sslProxy()
prx = Proxy()

call_twoway()
# call_timeout()
# call_extras()
call_async()
# call_oneway()
# call_bidirection()
tce.sleep(2)
sys.exit()



