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
		return 'Yah! '+text

	def timeout(self,secs,ctx):
		print 'enter timeout:',secs
		time.sleep( secs)

	def heartbeat(self,hello,ctx):
		print ctx.msg.extra.props
		print hello

	def bidirection(self,ctx):
		"""
		通过ctx 获取发送mq和user_id,发送推送调用到client端
		:return:
		"""
		epname = tce.Shortcuts.MQ_RETURN(ctx)
		user_id = tce.Shortcuts.USER_ID(ctx)
		print epname,user_id
		conn = tce.RpcCommunicator.instance().getConnectionMQCollection().get(epname)
		clientprx = ITerminalPrx(conn)
		clientprx.onMessage_oneway('server push message!',tce.Shortcuts.CALL_USER_ID(user_id))



def main():
	tce.RpcCommunicator.instance().init('server').initMQEndpoints('./config.yml')
	adapter  = tce.RpcAdapterMQ.create('adapter','mq_server')
	servant = ServerImpl()
	adapter.addServant(servant).start()
	tce.RpcCommunicator.instance().waitForShutdown()

if __name__ == '__main__':
	sys.exit( main())
