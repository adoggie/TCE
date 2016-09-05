package tce.android;

//import java.io.InputStream;
//import java.net.InetSocketAddress;
//import java.net.Socket;
//import java.nio.ByteBuffer;
//import java.nio.charset.Charset;
//import java.io.*;

//import tce.RpcAdapter;
//import tce.RpcCommunicator;
import tce.RpcMessage;
//import tce.RpcConnection;
import tce.RpcMessageXML;
import tce.RpcConnection_SocketXML;
import tce.android.RpcAsyncCommThread;
//import tce.RpcConnection_Socket;

public class RpcConnection_AsyncSocketXML extends  RpcConnection_SocketXML{

	
	RpcConnection_AsyncSocketXML(String host,int port){
		super(host,port);
		//_sock = new Socket();
	}
	
	@Override 
	protected void dispatchMsg(RpcMessage m){
		RpcAsyncCommThread.instance().dispatchMsg(m);
	}
	
	
	
	
}
