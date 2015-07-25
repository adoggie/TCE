
tce for javascript
[websocket]


1.编写 xxx.idl
2.编写 ifx-index-list.txt ，指定接口索引编号, 默认时将生成所有接口对象的服务端代码，包括 xxx_delegate() 和 servant基类
	sns.IBaseServer=100,false
	sns.ITerminal= 201,true
	sns.ICtrlServer = 301,false
	以上配置指定不同接口的值，并且只有ITermnial接口生成 delegate()代码，因为在本地要实现ITerminal功能，以便接收server发送的Rpc请求

3.实现本地ITermnial功能

3.1 定义servant对象
	function MyTerminal(){
		this.onNotifyMessage = function(notify,ctx){
		};
	}
3.2 指定servant的基类
	MyTerminal.prototype = new ITerminal();

4. 初始化tce

	RpcCommunicator.instance().init();
	gwaprx = IGatewayAdapterProxy.create('ws://localhost:4003');
	msgprx = IMessagingServiceProxy.createWithProxy(gwaprx);

	var servant = new MyTerminal();
	adapter = RpcCommunicator.instance().createAdapter("test");
	adapter.addServant(servant);
	msgprx.conn.attachAdapter(adapter);

5. 接口调用
    接口参数
    foo_async = function(p1,p2,..,async,error,props,cookie){

    prxService.foo_async(p1,p2,..,
        function(result,prx,cookie){
            console.log('cookie is:'+cookie);
        },
        function(){
    	    console.log('send failed!');
        },{},cookie
    );

websocket with ssl:
  wss://localhost:4003


**注意项***

1.  websocket接收到的数据类型是 bytearray而不是str
    发送时也必须将str类型转成bytearray再发送

2. javascript的字符串类型是utf-16，发送时需转换成utf-8