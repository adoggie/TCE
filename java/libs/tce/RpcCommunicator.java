

package tce;

//import tce.android.*;

//import tce.RpcCommAdapterXML;
//import tce.RpcConnection_SocketXML;
//import tce.RpcConnection_Http;
//import tce.RpcAsyncCommThread;
//import tce.RpcConnection_AsyncSocketXML;
//import tce.RpcMessageAsyncDispatcher;



//import tce.mq.RpcConnection_QpidMQ;

import java.io.File;
import java.util.*;

public class RpcCommunicator implements Runnable{
	private final static int MAX_NUM_OF_CACHED_MESSAGE = 1000;
	public final  static String INITIALIZE_PROP_THREAD_NUM="thread_num";


	protected static RpcCommunicator _handle = null;

	private RpcLogger _logger = null;
	private HashMap<String,RpcCommAdapter> _adapters = new HashMap<String,RpcCommAdapter>();
	private int _sequence =0;

	private Vector<RpcMessage> _pendingMsgs = new Vector<RpcMessage>();
	private Vector<Thread>	_processThreads = new Vector<Thread>();
	private int _processThreadNum = 1;
	private int _callwait = 1000*30 ;  // 默认呼叫等待时间 30s
	private boolean _exiting = false;
	private String _sysDevId = null;
	private String _serverName ="";
	HashMap<Integer,RpcMessage> _msglist = new HashMap<Integer,RpcMessage>();

	
	public RpcCommunicator(){
		setLogger(new RpcLogger());
//		init();
	}
	
	public static  RpcCommunicator instance(){
		if(_handle == null){
			_handle = new RpcCommunicator();
			//_handle.init();
		}
		return _handle;
			
	}

	public String getServerName(){
		return _serverName;
	}

	public int getProperty_DefaultCallWaitTime(){
		return _callwait;
	}
	
	public void setProperty_DefaultCallWaitTime(int value){
		_callwait = value;
	}
	
	public void setLogger(RpcLogger logger){
		_logger = logger;
	}
	
	public RpcLogger getLogger(){
		return _logger;
	}
	
	public int getUniqueSequence(){
		if(_sequence >= Integer.MAX_VALUE - 0xffff){
			_sequence = 0;
		}
		return ++_sequence;
	}

	void enqueueMessage(int sequence,RpcMessage m){
		synchronized(_msglist){
			_msglist.put(sequence,m);
		}
	}

	RpcMessage dequeueMessage(int sequence){

		Integer key = sequence;
		RpcMessage m =null ;
		synchronized(_msglist){
			if( _msglist.containsKey(key) ){
				m = _msglist.get(key);
				_msglist.remove(key);
			}
		}
		return  m;
	}

	synchronized void onConnectionDisconnected(RpcConnection conn){
		synchronized(this._msglist){
			for( RpcMessage m: _msglist.values()){
				try{
					if( conn == m.conn){
						_msglist.remove( m.sequence );
						synchronized(m){
							m.errcode = RpcConsts.RPCERROR_CONNECTION_LOST;
							m.notify();
						}

					}
				}catch(Exception e){
					RpcCommunicator.instance().getLogger().error(
							e.getMessage()
					);
				}
			}
		}
	}
	/*
	synchronized
	public void addConnection(RpcConnection conn){
		_conns.add(conn);
	}
	
	synchronized 
	public void removeConnection(RpcConnection conn){		
		for(RpcConnection n:this._conns){
			if( n == conn){
				_conns.remove(conn);
				break;
			}					
		}
	
	}
	*/

	public String getSystemDeviceID(){

		return _sysDevId;

	}

	public void setSystemDeviceID(String deviceId){
		_sysDevId = deviceId;
	}

	
	public RpcCommunicator init(String name, HashMap<String,String> properties){
		_serverName = name;

		if(properties!=null){
			if( properties.containsKey(INITIALIZE_PROP_THREAD_NUM)){
				String value = properties.get("thread_num");
				_processThreadNum = Integer.valueOf(value);
			}
			//分配线程
			for(int n=0;n<_processThreadNum;n++){
				Thread thread = new Thread(this);
				_processThreads.add(thread);
				thread.start();
			}
		}
		return this;
	}

	@SuppressWarnings("unchecked")
//	public boolean initMQEndpoints(String ymlfile){
//
//		File file = new File(ymlfile);
//		if( !file.exists() ){
//			return false;
//		}
//		String servername = getServerName();
//
//		try{
//			Object obj = Yaml.load(file);
//			HashMap<String,RpcEndPoint> ep_defs = new HashMap<String, RpcEndPoint>();
//			HashMap<String,Object> node,root = (HashMap<String,Object>)obj;
//			ArrayList<Object> list;
//			node =(HashMap<String,Object>) root.get("common_defs");
//			list =(ArrayList<Object>)node.get("endpoints");
//
//			RpcEndPoint ep ;
//			for( Object epdef:list){
//				HashMap<String,Object> item = (HashMap<String,Object>)epdef;
//				String name =(String) item.get("name");
//				String host =(String) item.get("host");
//				int port = (Integer) item.get("port");
//				String address =(String) item.get("address");
//				String type = (String) item.get("type");
//				ep = new RpcEndPoint(name,host,port,address,type);
//				ep_defs.put( name,ep);
//			}
//			node =(HashMap<String,Object>) root.get(servername);
//			list =(ArrayList<Object>)node.get("endpoints");
//
//			HashMap< String,RpcConnection_QpidMQ> conns = new HashMap<String, RpcConnection_QpidMQ>();
//
////			ArrayList<RpcConnection_QpidMQ> connWrites = new ArrayList<RpcConnection_QpidMQ>();
////			RpcConnection_QpidMQ connRead = null;
//			RpcConnection_QpidMQ conn ;
//			for(Object o: list){
//				HashMap<String,Object> item = (HashMap<String,Object>)o;
//				String name = (String)item.get("name");
//				String af = (String)item.get("af_mode");
//				ep = ep_defs.get(name);
//				int af_mode = RpcEndPoint.AF_READ;
//				if( af.toLowerCase().equals( "af_write")){
//					af_mode = RpcEndPoint.AF_WRITE;
//				}
//				conn = RpcConnection_QpidMQ.create(ep,af_mode);
//				if(conn == null){
//					System.out.println("QpidMQ create failed! " + ep.name);
//					return false;
//				}
//				conns.put( name,conn);
//			}
//
//			node =(HashMap<String,Object>) root.get(servername);
//			list =(ArrayList<Object>)node.get("endpoint_pairs");
//			for(Object o: list){
//				HashMap<String,Object> item = (HashMap<String,Object>)o;
//				String call = (String)item.get("call");
//				String return_ = (String)item.get("return");
//				conn = conns.get(call);
//				RpcConnection_QpidMQ connRead = conns.get(return_);
//				conn.setLoopbackMQ(connRead);
//				if( connRead == null){
//					System.out.println("QpidMQ not defined! "+ return_);
//				}
//			}
//
//		}catch (Exception e){
//			return false;
//		}
//		return true;
//	}
	

	public  int waitForShutdown(){
		for(RpcCommAdapter adapter:_adapters.values()){
			adapter.join();
		}
		try{
			for(int n=0;n<_processThreads.size();n++){
				Thread thread = _processThreads.get(n);
				thread.join();
			}
		}catch (Exception e){
			e.printStackTrace();
		}
		return 0;
	}
	
	public void shutdown(){
		_exiting = true;
		for(RpcCommAdapter adapter:_adapters.values()){
			adapter.close();
		}
	}
	
	/**
	 *
	 */
	public RpcCommAdapter createAdapterWithProxy(String id,RpcProxyBase proxy){
		RpcCommAdapter adapter = null;
//		if( type == RpcConsts.MSG_ENCODE_XML){
//			return new RpcCommAdapterXML(id);
//		}
		adapter = new RpcCommAdapter(id);
		proxy.conn.setAdapter(adapter);	
//		adapter.addConnection(proxy.conn);
		addAdatper(adapter);
		return  adapter;
	}
	
	public void addAdatper(RpcCommAdapter adapter){
		if(_adapters.containsKey(adapter.get_id())){
			return ;
		}
		_adapters.put(adapter.get_id(), adapter);
	}
	
	public RpcCommAdapter createAdapter(String id){
		RpcCommAdapter adapter = new RpcCommAdapter(id);
		addAdatper(adapter);
		return  adapter;
	}
	
	public RpcConnection createConnection(int type,String host,int port){
		if( (type&RpcConsts.CONNECTION_SOCK) !=0 ){
			if( (type & RpcConsts.CONNECTION_SSL)!=0) {
				return new RpcConnection_Socket(host,port,true);
			}
			return new RpcConnection_Socket(host,port,false);
		}
		return null;
	}

	@Override
	public void run(){
		while(!_exiting){
			RpcMessage m = null;
			synchronized (_pendingMsgs){
				try{
					if( _pendingMsgs.size() !=0){
						m = _pendingMsgs.remove(0);
					}else{
						_pendingMsgs.wait();
						if( _pendingMsgs.size() !=0){
							m = _pendingMsgs.remove(0);
						}
					}
				}catch (Exception e){
					e.printStackTrace();
				}
			}
			if(m !=null){
//				System.out.println("current thread id:"+ Thread.currentThread().getId());
				m.conn.dispatchMsg(m);
			}
		}
		RpcCommunicator.instance().getLogger().info("ProcessThread in Communicator:"+Thread.currentThread().getId()+" exited!");
	}


	public  void dispatchMsg(RpcMessage m){
		//block recv-thread
		while(_pendingMsgs.size()>MAX_NUM_OF_CACHED_MESSAGE){
			try{
				Thread.sleep(100);
			}catch (Exception e){
				e.printStackTrace();
			}
		}

		synchronized (_pendingMsgs){
			_pendingMsgs.add(m);
			_pendingMsgs.notify();
		}
	}
}
		
