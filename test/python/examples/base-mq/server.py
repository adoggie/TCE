#--coding:utf-8--


import os,os.path,sys,struct,time,traceback,signal,threading
sys.path.insert(0,'../../../../python')

from gevent import monkey
monkey.patch_all()

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
		print hello

	def bidirection(self,ctx):
		"""
		not supported in message-queue scene.
		birection适用在 链路双向复用的场景 ,例如: socket
		:return:
		"""
		pass
		# self.clientprx = ITerminalPrx(ctx.conn)
		# self.clientprx.onMessage_oneway('server push message!')



def main():
	tce.RpcCommunicator.instance().init('server').initMQEndpoints('./config.yml')
	adapter  = tce.RpcAdapterMQ.create('adapter','mq_server')
	servant = ServerImpl()
	adapter.addServant(servant).start()
	tce.RpcCommunicator.instance().waitForShutdown()

if __name__ == '__main__':
	sys.exit( main())
