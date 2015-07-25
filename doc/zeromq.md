# zeromq 

>tce 增加对zeromq的支持

##1. PUB and SUB
pub/sub提供amqp的topic功能


##PUSH and PULL
push/pull提供`amqp`的queue功能 


# 在zeromq上实现rpc

在使用amqp时，通过消息队列名称来区分消息的接收者。可zeromq只有sub模式时可以设定filter来接收自己消息，push/pull又该如何来区分呢？

zmq一个消息队列需要单独的通信endpoint (例：tcp://*:5500)来定义，这点不同amqp是提供一致的通信端点，内部提供消息交换队列。

系统如果存在大量消息队列，则要定义对应的不同的通信连接点endpoint

## Endpoint定义 

	<ep name="server1" address="queue:tcp://192.168.10.1:5566%tcp://192.168.10.1:5567" type="zmq" />
	<ep name="server2" address="topic:tcp://192.168.10.1:5566%tcp://192.168.10.1:5567" type="zmq" />


+ server1 - `push/pull` mode 
+ server2 - `pub/sub` mode
***
<font color='blue'>address format - `queue_type:read_queue_name%write_queue_name` </font>

***
	


## broker / non-broker
zeromq的broker要自编写，tce支持有broker和没有broker的情况。 小规模应用或者只是demo，无需设置单独的broker。

###no-broker
没有broker的情况下，消息交换的双方必须知道对方的连接端点信息。这种情况仅适用简单的网络模型，例如: 1 x N 或者 N x 1 的部署，要提供 N x N 的消息交换必须加入broker

在之前的项目中，如果系统服务只部署1个gws和1个mexs，1个userserver情况下就适用no-broker模式， 只需gws进行服务bind(),其他服务只需连接到gws的endpoint.

	<server name="direct_2" type="DIRECT" id="2" >
		<route if="IAuthService">
			<call in="direct_websocket" out="mq_cts_1"/>
			<return in="mq_direct_2" out="direct_websocket"/>
		</route>
		<extra_mqs ins="" outs=""/>
	</server>

* `in / ins` - 这种类型的endpoint在本地服务中需要进行bind()操作

