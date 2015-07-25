#--coding:utf-8--

import os,os.path,sys,struct,time,traceback,time,threading
sys.path.insert(0,'../../../../python')

from gevent import monkey
monkey.patch_all()

import tcelib as tce
from test import *



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

	prx.echo_async('pingpang',hello_callback_async,'cookie')


#传递附加数据
def call_extras():
	print prx.echo("hello",extra={'name':'scott.bo'})


def call_oneway():
	prx.heartbeat_oneway('hello world!')

def call_bidirection():
	"""
	not support in message-queue scene.
	birection适用在 链路双向复用的场景 ,例如: socket
	:return:
	"""
	pass







tce.RpcCommunicator.instance().init('client').initMQEndpoints('./config.yml')

conn = tce.RpcCommunicator.instance().getConnectionMQCollection().get('mq_server')
prx = ServerPrx(conn)


call_twoway()
# call_timeout()
# call_extras()
# call_async()
# call_oneway()


tce.sleep(2)



