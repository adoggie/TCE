package tce.android;


import tce.RpcConnection_Socket;
//import java.nio.charset.Charset;
import tce.RpcMessage;
import tce.android.RpcAsyncCommThread;

public class RpcConnection_Socket_Android extends RpcConnection_Socket{
	
	public RpcConnection_Socket_Android(String host,int port,boolean ssl_enable){
		super(host,port,ssl_enable);
	}
	
	@Override
	protected void dispatchMsg(RpcMessage m){
		RpcAsyncCommThread.instance().dispatchMsg(m);
	}
	
	@Override
	public  boolean sendMessage(RpcMessage m){
		if( m.status !=0){
			return super.sendMessage(m);
		}
		m.status = 1;
		return RpcMessageAsyncDispatcher.instance().sendMessage(m);
	}
	
	
	
}
