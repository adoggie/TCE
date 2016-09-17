
#1. 开始 
想到增加csharp的支持，缘与朋友公司使用unity开发手游，因为unity默认开发语言是c＃，当我摆弄unity入迷的时候，发现网络通信功能代码必须重新编写。要利用之前tce的结构，就必须在tce中增加对c＃的支持，耐着性子，开始工作。

毕竟从来没有接触过c＃语言，从基础的语法开始到框架设计的思考，2周时间，终于完成c＃版本，可以说这次开发，完全参考了之前tce对其它程序语言的时间，特别是java，毕竟C＃与java太过于相像了，很多代码直接复制到c#即可。 毕竟是重新实现的语言，从一开始考虑的比较全面，也是最顺畅的一次语言的扩展，也可以说是质量最高的一次。 

C＃的支持，开发工作主要是两部分： 
 	
 	1. tmake 编译程序的开发，通过编译idl生成对应的c＃框架代码，包括：proxy和 interface
 	2. C＃通信框架代码实现 (communicator,adapter,proxy,servant,accept,connection .. )
 	
#2. IDL定义 


##2.1 基础类型
	
	tce -> C#
	---------------
    byte 	=> byte 
    bool 	=> bool
    short 	=> short 
    int   	=> int
    float 	=> float 
    long  	=> long 
    double 	=> double 
    string 	=> string 
    void   	=> void 
    

##2.2 Sequence

c#的数组采用 List<>实现 sequence<>

idl:

    sequence<string> namelist_t;
    void collect_names( namelist_t names); 

C#:

    void collect_name( List<string> names);
        
##2.3 字节数组byte[]

对于字节数组类型,直接采用C＃的 byte[], 应用在对二进制流读写处理场景

idl:

    sequence<byte> StreamBytes_t;
    StreamBytes_t  bytes;
    void writeBytes( StreamBytes_t content);
C#:

    byte [] bytes;
    void writeBytes( byte[] content);
    

##2.4 Dictionary 
C#的字典类型采用 Dictionary<k,k> 实现 dictionary<k,v>.

< k >必须是tce的简单类型之一 (byte,bool,short,int,float,long,double,string)

idl :

    dictionay<string,string> Properties_t;
    void setProps(Properties_t props);
    
C#: 
    
    void setProps( Dictionary< sString, string > props)

##2.5 Struct
struct被映射为C#的class 

idl:

    sequence<int> intlist_t ;
    struct Student{
        int  id;
        intlist_t attrs;
        string  name;
    }
    
    dictionary< int , Student> StudentList_t;
    
    StudentList_t getStudents(int max);

C#: 
    
    class Student{
        int  id;
        List<int> attrs;
        string name;
    }
    
    Dictionary<int,Student> getStudents(int max);
    
##2.6 Interface
interface 声明服务接口，C＃实现采用`class`  

idl
    
    struct time_t{
        int year;
        int month;
        int day;
    }
    
    interface NtpServer{
        time_t syncDateTime();
    }

C#

    class time_t{
        int year;
        int month;
        int day;
    }
    
    class NtpServer{
        time_t syncDateTime();
    }
    
#### 接口继承

tce
    
    interface MyServer extends NtpServer{
        ... 
    }

C#

    class MyServer: NtpServer{
    }
    
    
##2.7 Module
module在C＃中对应的就是 `namespace`


#3. 编写一个TCE程序 

###3.1 定义接口

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


###3.2 tmake编译
	
	tce2csharp.py -i $TCE/idl/test.idl -o
	
	tmake 将生成框架代码 [test]

    
###3.3 编写服务端程序

C＃目前并不支持编写服务器侧代码，原因在于未找到合适的NIO处理方案。客户端程序直接使用OIO方式同步进行socket的数据发送和接收。 

服务器侧代码直接使用python的server代码： 
	
	$TCE/test/python/examples/simple/server.py 
	其运行之后，侦听 16005端口接受服务
	
###3.4 编写客户端程序 
	
	
	namespace simple{
	
	
    class TerminalImpl : ITerminal {
    
    	//此方法将被server调用
        public override void onMessage(string message, RpcContext ctx) {
            base.onMessage(message, ctx);
            Console.WriteLine( message);
        }
    }
    

    class Program {
        private ServerProxy prx = null;

		//发起一个反向调用，server接收到此消息之后反向在同一个连接上调用客户端程序 ITerminal.onMessage()接口
        void bidirection() {
            prx.bidirection_oneway();
        }
		
		//柱塞式调用，等待返回，但其内部还是会有超时控制
        void two_way() {
            Console.WriteLine("echo wall:" + prx.echo("hello tce! "));
        }
		
		//单向调用，只有函数类型为void，tce才能产生 xxx_oneway的接口函数
        void one_way() {
            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name", "scott");
            prx.heartbeat_oneway("hello man!",props);
        }

		//异步调用，用户需提供一个委托函数来接收返回值
        void async_call() {
            prx.echo_async("this is async test.", delegate(string result, RpcProxyBase proxy, object cookie) {
                Console.WriteLine("you recieved one async result:"+ result + " cookie is:" + cookie);                
            },null,"9680");
        }

		//调用传递额外附加参数
        void call_extradata() {
            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name", "scott");
            Console.WriteLine("echo wall:" + prx.echo("hello tce! ", 30000, props));
        }

        void init() {
        	//初始化日志输出到终端
            RpcCommunicator.instance().logger.addLogHandler("stdout", new RpcLogHandlerStdout());
            RpcCommunicator.instance().initialize("server1"); //初始化通信器
            RpcCommunicator.instance().settings.callwait = 1000*1000; //设置默认同步调用等待超时时间

            RpcAdapter adapter = RpcCommunicator.instance().createAdapter("adapter1"); //创建适配器
            prx = ServerProxy.create("192.168.199.235", 16005, false);  //创建一个服务对象的访问接口对象
            TerminalImpl impl = new TerminalImpl();   // 创建一个本地服务对象（提供server反向调用）
            adapter.attachConnection(prx.conn);       //将连接关联到适配器
            adapter.addServant(impl);  		 //将服务对象加入适配器

        }

        static void Main(string[] args) {
            Program program = new Program();
            program.init();
            for (int n = 0; n < 1; n++) {
                program.two_way();
                program.one_way();
                program.async_call();
                program.bidirection();
            }
            RpcCommunicator.instance().waitForShutdown();
            
        }
    }
}


####注意： 
C＃版本的Rpc发起的调用，必须进行异常捕获，由于C＃的函数原型不能如java一样可以声明 throws Exception，所以使用时必须注意。 

#4. 了解调用模型 
###4.1 异步调用 
tce将为proxy对象自动生成调用服务接口的异步函数 xxxx_async(...).

异步调用函数原型:  

	void xxx_async( p1,p2,..,delegate(result,RpcProxy proxy,object cookie ))

	p1,p2均为接口参数
	delegate() 的result指的是接口服务函数的返回值类型
	proxy,cookie 用于上下文的判别，cookie可以理解为user_data
	
	用户在使用异步调用接口函数时执行的线程Thread,与 异步返回delegate()的函数线程是不同的，需要通过cookie来进行两个现场之间上下文的传递(这是个tip). 
	
####注意 
声明为 `void`类型的接口函数，在声明delegate时，是不具有result参数的，例如: 

	idl: 
		interface Server{
			void hello(string text);
			string echo(string text);
		}
		
	生成的 Proxy代理函数原型: 
	    class ServerProxy{	    	
	    	public void hello_async(string text,delegate(RpcProxy proxy,object cookie),Dictionary<string,string> props,object cookie);
	    	public void echo_async(string text,delegate(string result,RpcProxy proxy,object cookie),Dictionary<string,string> props,object cookie);
	    }


####4.2 异步调用: 
	
	RpcProxy proxy = ServerProxy.create(conn);
	proxy.echo_async("hello",delegate(string result,RpcProxy proxy,object cookie){
		print "result:",result ," cookie:",cookie 
	},null,"1001");
		
	
####4.3 Promise

    void async_call() {
        RpcPromise p = new RpcPromise();
        p.then(_ => {
            prx.echo_async("this is a sync text",
                delegate(string result, RpcAsyncContext ctx) {
                    Console.WriteLine("echo() result:" + result);
                    ctx.promise.data = result;
                    ctx.onNext();
                }, _.promise);
        }).then(_ => {
            prx.timeout_async(1, delegate(RpcAsyncContext ctx) {
                Console.WriteLine("timeout completed!");
                ctx.onNext();    
            },_.promise);                
        });
        RpcPromise pe = p.error(_ => {
            Console.WriteLine("async call error:"+ _.exception.ToString());
            _.onNext();
        });
        p.final(_ => {
            Console.WriteLine(" commands be executed completed!");
        });
        p.end();
    }
