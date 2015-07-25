#--coding:utf-8--


import os,os.path,sys,struct,time,traceback,signal,threading
sys.path.insert(0,'../../../../python')

from gevent import monkey
monkey.patch_all()

import tcelib as tce
from sns import *

class GatewayServer:
	def __init__(self):
		self.mq_name = None

gws_mqs={
	'gwserver':'mq_gateway',
	'gwserver_ws':'mq_gateway_ws'
}

class MessageServerImpl(IMessageServer,):
	def __init__(self):
		IMessageServer.__init__(self)
		self.clientprx = None
		self.user_mq ={}


	def onUserOnLine(self, user_id,gws_name, ctx):
		print 'user  online:',user_id,' from:',gws_name
		self.user_mq[user_id] = gws_mqs.get(gws_name)

	def onUserOffLine(self, user_id, gws_name,ctx):
		print 'user  offline:',user_id,' from:',gws_name
		del self.user_mq[user_id]

	def postMessage(self, target_user_id, msg, ctx):
		user_id = tce.Shortcuts.USER_ID(ctx)
		print '-'*20
		print ctx.msg.extra.props
		print 'from:',user_id
		print 'target:',target_user_id
		print 'message:',msg.content

		mq = self.user_mq.get(target_user_id)
		if not mq:
			print 'target user is offline,',target_user_id
			return
		epname = mq
		user_id = target_user_id # tce.Shortcuts.USER_ID(ctx)
		print epname,user_id
		conn = tce.RpcCommunicator.instance().getConnectionMQCollection().get(epname)
		clientprx = ITerminalPrx(conn)
		msg.sender_id = user_id
		msg.issue_time = 1000
		clientprx.onMessage_oneway(msg,tce.Shortcuts.CALL_USER_ID(user_id))

		print '-'*20


def main():
	tce.RpcCommunicator.instance().init('server').initMQEndpoints('./config.yml')
	adapter  = tce.RpcAdapterMQ.create('adapter','mq_server','mq_user_event_listener')
	servant = MessageServerImpl()
	adapter.addServant(servant).start()
	tce.RpcCommunicator.instance().waitForShutdown()

if __name__ == '__main__':
	sys.exit( main())
