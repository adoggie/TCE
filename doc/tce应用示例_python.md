### 多层结构的RPC调用示例

我把移动互联网实现分为三层，分别是: 

	用户交互层、网关接入层、应用服务层。 

在这里以python代码来做讲解，代码见 $tce/test/python/cluster

```
"client.py"  - 客户端程序，调用后端服务的接口 
"gateway.py" - 网关接入服务，负责在client与server之间的消息交换
"server.py"  - 内部服务程序，提供不同的功能接口

"qpid" 	平台内部系统交换消息的服务(MQ)

client与gateway的接口是socket, gateway与server之间通过mq进行传递。

```

###1.配置
首先要对各模块进行配置，配置文件涉及： services.xml 、 config.yml 

#### gateway 配置 
配置文件: services.xml

```
接口定义 
<InterfaceDef >
	<if id="0" name="test.BaseServer"/>
	<if id="1" name="test.ITerminalGatewayServer"/>
	<if id="2" name="test.Server"/>
	<if id="3" name="test.ITerminal"/>
</InterfaceDef>
InterffaceDef 定义了在gateway服务程序中需要交换的接口类型，包括：名称和编。
```

```
变量定义
<VariantDef>
	<var name="mq-host" value="centos66"/>
	<var name="mq-port" value="5672"/>
	<var name="gws_socket_host" value="localhost"/>
</VariantDef>
var变量会在配置文件的多处引用到。在引用时的格式 "{var_name}" ,例如：
 
<ep name="websocket_gateway" 	address="" type="websocket" host="{gws_socket_host}" port="12001" keyfile="" certfile=""/>

```
```
通信端点定义

	<EndPoints>
		<ep name="websocket_gateway" 	address="" type="websocket" 
				host="{gws_socket_host}" port="12001" keyfile="" certfile=""/>
		<ep name="socket_gateway" 	address="" type="socket" 
				host="{gws_socket_host}" port="12002" keyfile="" certfile=""/>
		<ep name="mq_gateway" 		address="mq_gateway;{create:always,node:{type:queue,durable:true}}" 
				type="qpid" host="{mq-host}" port="{mq-port}"/>
		<ep name="mq_gateway_ws" 		address="mq_gateway_ws;{create:always,node:{type:queue,durable:true}}" 
				type="qpid" host="{mq-host}" port="{mq-port}"/>
		<ep name="mq_server" 		address="mq_server;{create:always,node:{type:queue,durable:true}}" 
				type="qpid" host="{mq-host}" port="{mq-port}"/>
	</EndPoints>

通信端点类型有: websocket,socket,qpid 

websocket - 支持 html5的websocket连接接入 
socket 	- 支持 任意的以socket方式连接进入的客户端形式(android,ios,c++)
qpid  - gateway与sever的数据交换方式

```

```
服务器定义 
<servers>
		<server name="gwserver"  type="socket server">
			...
		</server>
		<server name="gwserver_ws"  type="websocket server">
			...
		</server>
</servers

gwserver、gwserver_ws是两种通信接入方式的网关服务器配置项，

```
####server配置
配置文件 config.yml

```
common_defs:
  endpoints:
    - name: mq_gateway
      host: centos66
      port: 5672
      address: mq_gateway;{create:always,node:{type:queue,durable:true}}
      type: qpid
      
server:
  endpoints:
    - name: mq_gateway
      af_mode: AF_WRITE
    - name: mq_server
      af_mode: AF_READ
    - name: mq_gateway_ws
      af_mode: AF_WRITE

`server` 定义了使用到的 endpoints,这些endpoints对于server来讲是可读或者可写的。
      
```

### 2.运行
运行步骤：

```
1.编写test.idl
2.编译idl
   python $tce/tce2py.py -i test.idl ./
   生成python的骨架文件 test.py
3.执行 
	1. 启动qpid服务，默认: localhost:5672 ,  确保services.xml的 `mq_host`和`port`项正确配置
	2. 运行server ， python server.py 
	3. 运行gateway,  python gateway.py gwserver    #socket接入
	4. 运行client ,  python client.py   # client.py已指定gateway的通信端口 tcp://localhost:12002
   
```

### 3.代码解析
#####1. 接口定义 

接口文件 :  $tce/idl/test.idl 

```
module test{

	interface BaseServer{
		string datetime();
	};

	interface ITerminalGatewayServer{
		void ping();
	};

	interface Server extends BaseServer{
		string echo(string text);
		void  timeout(int secs);
		void heartbeat(string hello);
		void bidirection();
	};

	interface ITerminal{
    	void onMessage(string  message);
	};

}

client  - 实现ITerminal接口，提供server的反向调用; 
gateway - 实现 ITerminalGatewayServer 网关接口 
server  - 实现 Server 功能接口 

```
#####2. server代码

```
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
	
```

#####3.client 代码

```

class TerminalImpl(ITerminal):
	def __init__(self):
		ITerminal.__init__(self)

	def onMessage(self,message,ctx):
		#这里接收server推送的消息
		print 'onMessage:',message

def call_twoway():
	print prxServer.echo("hello")

def call_timeout():
	try:
		print prxServer.timeout(3,6)
	except tce.RpcException, e:
		print e.what()

def call_async():
	# python方式的异步回调接口
	def hello_callback_async(result,proxy,cookie):
		print 'async call result:',result
		print 'cookie:',cookie

	prxServer.echo_async('pingpang',hello_callback_async,'cookie')


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
	#触发server进行反向调用
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


tce.RpcCommunicator.instance().init()  #初始化tce库
prxServer,prxGWS = Proxy() 				#获取访问代理

call_twoway()	#执行调用
tce.sleep()
```

        
