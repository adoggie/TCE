#-- coding:utf-8 --

#模拟 Ts服务器，收发xml消息

import time,os,sys,os.path,socket,struct,traceback
from xml.dom.minidom import getDOMImplementation
import xml.dom.minidom

CALL = 0x01
RETURN = 0x02
TWOWAY = 0x10
ONEWAY = 0x20
ASYNC = 0x40

LISTEN = ('',12001)

PACKET_TAIL = '</NaviMSG>'

class SnsServer:
	def __init__(self):
		self.sock = None
		self.buf = ''

	def parse(self,d,c):
		domlist=[]

		self.buf += d
		while self.buf:
			end = self.buf.find(PACKET_TAIL)
			if end == -1:
				return domlist
			begin = self.buf.find('<NaviMSG')
			if begin == -1:
				self.buf = end + len(PACKET_TAIL)
				return domlist
			d = self.buf[begin:end+len(PACKET_TAIL)]
			self.buf =  self.buf[end+len(PACKET_TAIL) :]
			try:
				print 'got:',d
				dom = xml.dom.minidom.parseString(d)
				domlist.append(dom)
			except:
				print 'xml parse error!'
				return []
		return domlist
#				traceback.print_exc()

	def process(self,e,c):
		seq = e.getAttribute("sequence")
		type = e.getAttribute('type')
		calltype = int(e.getAttribute("calltype"))
#		print type(calltype)
		print seq,type,calltype
		if type == 'heartbeat':
			#发送进入，准备反向调用
			xml = '''
			<NaviMSG msgcls="Terminal" msg="Terminal.hello" type="Terminal.hello"
			calltype="%s" sequence="1"><User token=""/></NaviMSG>
			'''%(CALL|TWOWAY)
			c.sendall(xml)
			print 'send back:',xml

		if type == 'verify':
			xml='''
			<NaviMSG type="verify_res" calltype="2" sequence="%s">
			<Result code="0">
				<User id="scott"/>
				<Groups>
					<Group id="1" name="li" type="circle"/>
					<Group id="2" name="wang" type="circle"/>
				</Groups>
			</Result>
			</NaviMSG>
			'''%(seq)

			xml='''
			<NaviMSG type="verify_res" calltype="2" sequence="%s">
			<Result code="0">
				<User id="scott"/>
			</Result>
			</NaviMSG>
			'''%(seq)
#			time.sleep(3) #delay
			c.sendall(xml)
			print 'send back:',xml


	def start(self):
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		self.sock.bind(LISTEN)
		self.sock.listen(5)
		print 'serve on:',LISTEN
		while True:
			print 'ready for new client..'
			c,addr = self.sock.accept()
			print 'incoming ',addr
			self.buf = ''
			try:
				while True:
					d = c.recv(1000)
					if not d: break
					print d
					doms = self.parse(d,c)

					for dom in doms:
						self.process(dom.documentElement,c)
					c.close()					
					break
			except :
				traceback.print_exc()



SnsServer().start()