#--coding:utf-8--


import os,os.path,sys,struct,time,traceback,signal,threading
sys.path.insert(0,'../../../../python')
import tcelib as tce
from test import *


class ServerImpl(Server):
	def __init__(self):
		Server.__init__(self)
		self.clientprx = None

	def echo(self, text, ctx):
		print 'extra oob data:',ctx.msg.extra.props
		return text

	def timeout(self,secs,ctx):
		print 'enter timeout:',secs
		time.sleep( secs)

	def heartbeat(self,hello,ctx):
		print ctx.msg.extra.props
		print hello

	def bidirection(self,ctx):
		"""
		not supported in message-queue scene.
		birection适用在 链路双向复用的场景 ,例如: socket
		:return:
		"""
		self.clientprx = ITerminalPrx(ctx.conn)
		self.clientprx.onMessage_oneway('server push message!')


def simple_test_ssl():
	tce.RpcCommunicator.instance().init('server')
	ep = tce.RpcEndPoint(host='',port=16005,ssl=True,keyfile='server.key', certfile='server.crt')
	adapter = tce.RpcCommunicator.instance().createAdapter('first_server',ep)
	servant = ServerImpl()
	adapter.addServant(servant)
	tce.RpcCommunicator.instance().waitForShutdown()

def simple_test_websocket(ssl=False):
	tce.RpcCommunicator.instance().init('server')
	if ssl:
		ep = tce.RpcEndPoint(host='',port=16006,ssl=True,type_='websocket',keyfile='server.key', certfile='server.crt')
	else:
		ep = tce.RpcEndPoint(host='',port=16006,ssl=False,type_='websocket')
	adapter = tce.RpcCommunicator.instance().createAdapter('first_server',ep)
	servant = ServerImpl()
	adapter.addServant(servant)
	tce.RpcCommunicator.instance().waitForShutdown()



def simple_test():
	tce.RpcCommunicator.instance().init('server')
	ep = tce.RpcEndPoint(host='',port=16005,type_='socket')
	adapter = tce.RpcCommunicator.instance().createAdapter('first_server',ep)
	servant = ServerImpl()
	adapter.addServant(servant)
	tce.RpcCommunicator.instance().waitForShutdown()

def main():
	simple_test()

if __name__ == '__main__':
	main()
