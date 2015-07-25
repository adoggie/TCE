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
	print prxServer.echo("hello")


def call_timeout():
	try:
		print prxServer.timeout(3,6)
	except tce.RpcException, e:
		print e.what()


def call_async():

	def hello_callback_async(result,proxy,cookie):
		print 'async call result:',result
		print 'cookie:',cookie

	prxServer.echo_async('pingpang',hello_callback_async,'cookie')


#传递附加数据
def call_extras():
	print prxServer.echo("hello",extra={'name':'scott.bo'})


def call_oneway():
	prxServer.heartbeat_oneway('hello world!')


def call_bidirection():
	adapter = tce.RpcCommAdapter('adapter')
	impl = TerminalImpl()
	adapter.addConnection(prxServer.conn)
	adapter.addServant(impl)
	tce.RpcCommunicator.instance().addAdapter(adapter)

	# prxGWS.ping_oneway()
	prxServer.bidirection_oneway()

def Proxy():
	"""
	获得代理
	:return:
	"""
	ep = tce.RpcEndPoint(host='localhost',port=12002)
	prx_server = ServerPrx.create(ep)
	prx_gws = ITerminalGatewayServerPrx.createWithProxy(prx_server)
	return prx_server,prx_gws



tce.RpcCommunicator.instance().init()
prxServer,prxGWS = Proxy()

# prxGWS.ping_oneway()

# call_twoway()
# call_timeout()
# call_extras()
call_async()
# call_oneway()
# call_bidirection()
tce.sleep(2)
sys.exit()



