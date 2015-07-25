#--coding:utf-8--

import os,os.path,sys,struct,time,traceback,time
sys.path.insert(0,'../../../../python')
import tcelib as tce
from sns import *


class TerminalImpl(ITerminal):
	def __init__(self):
		ITerminal.__init__(self)

	def onMessage(self,message,ctx):
		print 'onMessage:',message,' from message server!'
		print '-'*10, 'message content', '-'*10
		print 'sender:',message.sender_id
		print 'content:',message.content



CURRENT_USER_ID = 'A1001'
TARGET_USER_ID = 'A1002'

def send_message():

	target = ''
	text = ''
	if len(sys.argv) >=2:
		target = sys.argv[1]
		text = sys.argv[2]
	if not target or not text:
		print 'please give message reciever and message content !'
		return

	try:
		target = target.upper()

		msg = Message_t()
		msg.content = text #'this is a short message from python client!'

		def callback_result(prx,cookie):
			print 'postMessage has sent message to server!'

		prxServer.postMessage_async(target,msg,callback_result)
	except tce.RpcException, e:
		print e.what()



def Proxy():
	"""
	获得代理
	:return:
	"""
	ep = tce.RpcEndPoint(host='localhost',port=12002)
	prx_server = IMessageServerPrx.create(ep)
	prx_gws = ITerminalGatewayServerPrx.createWithProxy(prx_server)
	prx_server.conn.setToken(CURRENT_USER_ID)
	#设定用户身份,gws将在连接进入第一个消息包对身份进行验证
	return prx_server,prx_gws


tce.RpcCommunicator.instance().init()
prxServer,prxGWS = Proxy()

adapter = tce.RpcCommAdapter('adapter')
impl = TerminalImpl()
adapter.addConnection(prxServer.conn)
adapter.addServant(impl)
tce.RpcCommunicator.instance().addAdapter(adapter)



prxGWS.ping_oneway()

send_message()

# tce.sleep(2)
print 'Current User ID: ',CURRENT_USER_ID
tce.waitForShutdown()
sys.exit()

# usage：
#   python client.py A1002 "hello world!"

