

package tce;



import java.util.*;

public class RpcCommunicator implements RpcMessageDispatcher.Client{
	private final static int MAX_NUM_OF_CACHED_MESSAGE = 1000;
	public final  static String INITIALIZE_PROP_THREAD_NUM="thread_num";

	public class Settings{
		public String name;
		public int callwait = 1000*30 ;
		public int threadNum = 1;
	}

	protected static RpcCommunicator _handle = null;

	private RpcLogger _logger = null;
	private HashMap<String, RpcAdapter> _adapters = new HashMap<String, RpcAdapter>();
	private int _sequence =0;


	Settings _settings = new Settings();
	private boolean _exiting = false;
	private String _sysDevId = "dev-xxx:";
	private String _serverName ="";
	HashMap<Integer,RpcMessage> _msglist = new HashMap<Integer,RpcMessage>();
	RpcMessageDispatcher _dispatcher ;
	
	public RpcCommunicator(){
		setLogger(new RpcLogger());
	}
	
	public static  RpcCommunicator instance(){
		if(_handle == null){
			_handle = new RpcCommunicator();
		}
		return _handle;
			
	}

	public String getServerName(){
		return _serverName;
	}

	public int getProperty_DefaultCallWaitTime(){
		return _settings.callwait;
	}

	public Settings getSettings(){
		return _settings;
	}

	public void setProperty_DefaultCallWaitTime(int value){
		_settings.callwait = value;
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

	public String getSystemDeviceID(){

		return _sysDevId;

	}

	public void setSystemDeviceID(String deviceId){
		_sysDevId = deviceId;
	}

	
	public RpcCommunicator init(String name, HashMap<String,String> properties){
		_serverName = name;
		_settings.name = name;
		if(properties!=null){
			if( properties.containsKey(INITIALIZE_PROP_THREAD_NUM)){
				String value = properties.get("thread_num");
				_settings.threadNum = Integer.valueOf(value);
			}
		}

		_dispatcher = new RpcMessageDispatcher(this,_settings.threadNum);
		_dispatcher.open();
		return this;
	}

	public String getName(){
		return _settings.name;
	}


	public  int waitForShutdown(){
		for(RpcAdapter adapter:_adapters.values()){
			adapter.join();
		}
		_dispatcher.join();
		return 0;
	}
	
	public void shutdown(){
		_dispatcher.close();
		for(RpcAdapter adapter:_adapters.values()){
			adapter.close();
		}
	}
	
	public RpcAdapter createAdapterWithProxy(String id, RpcProxyBase proxy){
		RpcAdapter adapter = null;
		adapter = new RpcAdapter(id);
		proxy.conn.setAdapter(adapter);	
		addAdatper(adapter);
		return  adapter;
	}
	
	public void addAdatper(RpcAdapter adapter){
		if(_adapters.containsKey(adapter.getID())){
			return ;
		}
		_adapters.put(adapter.getID(), adapter);
	}
	
	public RpcAdapter createAdapter(String id){
		RpcAdapter adapter = new RpcAdapter(id);
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


	public  void dispatchMsg(RpcMessage m){
		_dispatcher.dispatchMsg(m);
	}

}
		
