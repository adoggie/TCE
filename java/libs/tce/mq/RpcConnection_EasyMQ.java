package tce.mq;

import tce.*;
import java.util.*;
import easymq.message_t;
import easymq.mq_handle_t;
import easymq.IServerProxy;


public class RpcConnection_EasyMQ extends tce.RpcConnection {
	public final static  int QUEUE = 0;
	public final static  int TOPIC = 1;
	public final static  int READ = 0x01;
	public final static  int WRITE = 0x02;
	public final static  int READWRITE = READ|WRITE;
	
	static HashMap<String,RpcConnection_EasyMQ> _mq_conns = new HashMap<String,RpcConnection_EasyMQ>();
	
	public static RpcConnection_EasyMQ create(String host,int port,String queueName,int readwrite){
		RpcConnection_EasyMQ conn;
		conn = new RpcConnection_EasyMQ( host, port, queueName, readwrite);
		synchronized(_mq_conns){
			String name = conn.getUnique();
			if(!_mq_conns.containsKey(name)){
				_mq_conns.put(name, conn);
			}
		}
		conn.open();
		return conn;
	}
	
	String getUnique(){
		String name="queue";
		if(this._type == RpcConnection_EasyMQ.TOPIC){
			name = "topic";
		}
		name +=":"+_queueName;
		return String.format("%s:%d %s",_host,_port,name);
	}
	
	class EasyMQ_ClientImpl extends easymq.IClient{
		private RpcConnection_EasyMQ _owner;
		
		EasyMQ_ClientImpl(RpcConnection_EasyMQ conn){
			super();
			_owner = conn;
		}
		
		@Override
		public void onRecvData(mq_handle_t mq, message_t msg, RpcContext ctx) {
			RpcMessage m = RpcMessage.unmarshall(msg.data);
			_owner.dispatchMsg(m);
		}
		
		void open(){
			
			
		}
		
		void close(){
			
		}
		
	}
	
	class BackWorker implements Runnable{
		RpcConnection_EasyMQ _owner;
		boolean _exit = false;
		Thread	_thread = null;
		public BackWorker(RpcConnection_EasyMQ owner){
			_owner = owner;
			_thread = new Thread(this);
			_thread.start();
		}
		
		public void run(){
			while(!_exit){
				try{
					Thread.sleep(1000*5);
					_owner._keepalive();
				}catch(Exception e){
					
				}
				
			}
		}
		
		void exit(){
			_exit = true;
		}
		
		void join(){
			try{
				_thread.join();
			}catch(Exception e){
				System.out.println(e.toString());
			}
		}
	}
	
	/*****
	 * 
	 */
	
	private Vector<Thread>  _threads = new Vector<Thread>();
	private Vector<message_t> _mq_msgs = new Vector<message_t>();
	private BackWorker _worker = null;
	private int _threadnum = 1 ;
	
	private RpcConnection_EasyMQ _buddy = null;
	private EasyMQ_ClientImpl _mqclient = null;
	private mq_handle_t _handle = null;
	
	private String _host ;
	private int _port;
	private String _queueName;
	private int _queueType;
	private int _readwrite;
	private boolean _exit = false;
	private IServerProxy _prx = null;
	private RpcAdapter _adapter;
	
	RpcConnection_EasyMQ(String host,int port,String queueName,int readwrite){
		super(host,port);
		_host = host;
		_port = port;
		_queueName = queueName;
		String[] ss = queueName.trim().split(":");
		String qtype = "queue";
//		String qname = ss[0];
		_queueName = ss[0];
		if(ss.length>1){
			qtype = ss[0];
			_queueName = ss[1];
		}
		_queueType = QUEUE;
		if( qtype =="topic"){
			_queueType = TOPIC;
		}
		
		_prx = IServerProxy.create(_host, _port);
//		_queueType = queueType;
		_readwrite = readwrite;
		_mqclient = new EasyMQ_ClientImpl(this);
		_mqclient.open();
		_adapter = RpcCommunicator.instance().createAdapter(getUnique()+" adapter-server");
		_adapter.addServant(_mqclient);
		_prx.conn.setAdapter(_adapter);
	}
	
	
	public static void setLoopbackMQ(RpcConnection_EasyMQ read,RpcConnection_EasyMQ write){
		write._buddy = read;
	}
	
	public void setThreadNumber(int number){
		_threadnum = number;		
	}
	
	@Override
	public void join(){
		try{
			for (Thread t:this._threads){
				t.join();
			}
			_worker.join();
			
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}
	}
	
	@Override
	public void open(){
		
		_worker = new BackWorker(this);		
		
		for(int n=0;n< this._threadnum;n++){
			Thread thread = new Thread(this);
			thread.start();
			_threads.add(thread);
			try{
//				while( thread.getState() == Thread.State.
			}catch(Exception e){
				System.out.println(e.toString());
			}
		}
		_do_open();
	}
	
	private synchronized void _do_open(){
		try{
			_prx.register("", 1000*5, null);
			_handle = _prx.openMQ(this._queueName,this._queueType, 1, this._readwrite, 1000*5, null);
			
		}catch(Exception e){
			_handle = null;
			System.out.println(e.toString());
		}
	}
	
	void _keepalive(){
		try{
			if(this._handle == null){
				_do_open();
			}
			_prx.heartbeat_oneway(null);
		}catch(Exception e){
			System.out.println(e.toString());
			_handle = null;
		}
	}
	
	// 接收消息的mq将消息回送到发送消息的mq对象上去，因为 缓存等待的消磁队列在 读消息队列上
	@Override
	protected void dispatchMsg(RpcMessage m){	
		m.conn = this;
		super.dispatchMsg(m);
	}
	
	@Override
	public void close(){
		_exit = true;
		_worker.exit();
	}
	
	@Override
	protected
	boolean sendDetail(RpcMessage m){
		if( (m.calltype & RpcMessage.RETURN) !=0 ){
			String mqname = m.callmsg.extra.getPropertyValue("__mq_return__");
			if(mqname == null){
				return false;
			}
			if(_readwrite == RpcConnection_EasyMQ.READ){
				synchronized(_mq_conns){
					if(_mq_conns.containsKey(mqname)){
						RpcConnection_EasyMQ conn = _mq_conns.get(mqname);
						return conn.sendDetail(m);
					}
				}	
			}
			if(_readwrite == RpcConnection_EasyMQ.WRITE){
				//-- 直接写消息到写队列
				easymq.message_t msg = new easymq.message_t();
				msg.data = m.marshall();
				try{
					_prx.writeMQ_oneway(_handle, msg, null);
				}catch(Exception e){
					System.out.println(e.toString());
					_handle = null;
					return false;
				}
				return true;
			}
			return false;
		}
		
		if( (m.calltype & RpcMessage.CALL)!=0){
			if(this._queueType != WRITE ){
				return false;
			}
			if( (m.calltype & RpcMessage.ONEWAY) == 0 && this._buddy == null){ //单向消息包
				System.out.println("read connection not defined!");
				return false;
			}
			if( (m.calltype & RpcMessage.ONEWAY) == 0){
				String mqname = _buddy.getUnique();
				m.extra.getProperties().put("__mq_return__", mqname); //设置接收消息队列
			}
			//-- 直接写消息到写队列
			easymq.message_t msg = new easymq.message_t();
			msg.data = m.marshall();
			try{
				_prx.writeMQ_oneway(_handle, msg, null);
			}catch(Exception e){
				System.out.println(e.toString());
				_handle = null;
				return false;
			}
			return true;
		}
		return false;
	}
	
	@Override 
	public void run(){
		message_t msg = null;
		while(!_exit){
			try{
				synchronized(this._mq_msgs){
					this._mq_msgs.wait(1000);
					if(this._mq_msgs.size() == 0){
						continue;
					}
					msg = _mq_msgs.remove(0);					
				}
				RpcMessage m = RpcMessage.unmarshall(msg.data);
				this.dispatchMsg(m);
			}catch(Exception e){
				System.out.println(e.toString());
			}
		}
		
	}
	
	
	
}
