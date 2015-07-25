

package tce.android;

import tce.RpcCommunicator;
import tce.RpcConnection;
import tce.RpcConsts;
import tce.android.RpcAsyncCommThread;
import tce.android.RpcConnection_Socket_Android;
import tce.android.RpcMessageAsyncDispatcher;

import java.util.HashMap;

public class RpcCommunicator_Android extends RpcCommunicator{
	
	public RpcCommunicator_Android(){
		super();
	}
	
	public static  RpcCommunicator instance(){
		if(_handle == null){
			_handle = new RpcCommunicator_Android();
			//_handle.init();
		}
		return _handle;
			
	}


	@Override
	public RpcCommunicator init(String name,HashMap<String,String> properties){
		RpcAsyncCommThread.instance();
		RpcMessageAsyncDispatcher.instance();
		return super.init(name,properties);
	}

	@Override
	public RpcConnection createConnection(int type, String host, int port) {
		if( (type&RpcConsts.CONNECTION_SOCK) !=0 ){
			if( (type & RpcConsts.CONNECTION_SSL)!=0) {
				return new RpcConnection_Socket_Android(host,port,true);
			}
			return new RpcConnection_Socket_Android(host,port,false);

		}
		return null;
	}
	
	
	
}
		
