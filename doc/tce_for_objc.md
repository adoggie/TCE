
###1.简介

tce为了丰富移动终端的覆盖，对ios设备的提供objc的开发支持。

目前tce仅提供client端的功能，tce保证开发者可以使用与android开发一致的编程接口与服务平台进行交互，同样无需关心底层的细节，例如： 数据序列化、传输、加密、分派等。

###2.实现移动端设备之间消息传送

	代码： 
		objc客户代码 :  	$tce/test/objc/test 
		服务器代码:   #tce/test/python/examples/sendmessage
		样例IDL:  	$tce/idl/sns.idl   

####编码设计

#####1.接口定义  sns.idl
	
	```
	module sns{

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
	struct Message_t{
		string sender_id;
		string issue_time;
		string content;
	};

	interface ITerminal{
    	void onMessage(Message_t  message);
	};

	interface IMessageServer{
		void onUserOnLine(string user_id,string gws_name);
		void onUserOffLine(string user_id,string gws_name);
		void postMessage(string target_user_id,Message_t msg);
	};
}
```

######2.objc代码 

1.定义通知消息接收接口 

```
@interface MyTerminal:ITerminal
	@property ViewController * viewController;
@end

@implementation MyTerminal
- (instancetype)init:(ViewController *)vc{
    self = [super init];
    if (self) {
        self.viewController = vc;
    }
    return self;
}

- (void)onMessage:(Message_t *)message context:(RpcContext *)ctx {
    NSLog(@"recieved message:%@",message.content);

    dispatch_queue_t mainQueue= dispatch_get_main_queue();
    dispatch_sync(mainQueue, ^{
        [self.viewController.edtRecieved setText:message.content] ;
    });
}
@end

```
2.初始化Rpc 

```
NSString* CURRENT_USER_ID = @"A1004";

-(void)initRpc{
	[[RpcCommunicator instance] initialize];
    self->_adapter = [[RpcCommunicator instance] createAdapter:@"adapter"];
    MyTerminal *servant = [[MyTerminal alloc] init:self];
    self->_prxServer = [IMessageServerProxy createWithInetAddressHost:@"192.168.199.176" andPort:12002];
    [self->_adapter addServant:servant];
    [self->_adapter addConnection:[self->_prxServer conn]];
    [[RpcCommunicator instance] addAdapter:self->_adapter];
    [[self->_prxServer conn] setToken:CURRENT_USER_ID];
}
	
```
3.发送通消息

```
 	Message_t *msg = [Message_t new];
    msg.content = self.edtContent.text;
    NSString * target = self.edtPeerId.text;
    [self->_prxServer postMessage_oneway:target msg:msg props:nil];
```


####运行：
	
1.运行服务程序

```
	python gateway.py 		- socket 网关
	python gateway.py gwserver_ws 	- websocket 网关
	python gateway.py server 	- 消息交换服务 
```
	
2.运行html5的移动网页客户端 
	
	$tce/websocket/test_sns_sendmessage.html
	    

3.根据idl生成objc框架代码  

```
	python tce2objc.py -i idl/sns.idl -o ./
	tce将生成 sns.h sns.mm 文件 ，并将其加入工程
```

4.编译运行，发送消息到test_sns_sendmessage.html接收，或总page发送到ios程序接收。终端之间消息传输通过服务器中转。 





