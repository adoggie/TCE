package tce;

import java.io.InputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.io.*;


public class RpcConnection_SocketXML extends  RpcConnection  implements Runnable {

	protected Socket 	_sock = null;
	
	protected ByteBuffer _buff;
	protected RpcAdapter _adapter = null;
	protected Thread 	_workthread = null;;
	
	public RpcConnection_SocketXML(String host,int port){
		super(host,port);
		//_sock = new Socket();
		_type = RpcConsts.CONNECTION_SOCK;
	}
	
	public void run(){
		try{
			//BufferedReader in = new BufferedReader( new InputStreamReader(_sock.getInputStream()));
			String strbuf ="";
			byte[] d = new byte[1024*5];
			InputStream is = _sock.getInputStream();
			int len;
			
			this.onConnected();
			
			while (true){				
				len = is.read(d);
				if(len < 0 ){
					RpcCommunicator.instance().getLogger().debug("Socket Lost!");
//					System.out.println("Socket Lost!");
					_sock.close();
					break;
				}
				
				//strbuf+= new String(d,0,len,Charset.forName("UTF-8")); //
				strbuf+= new String(d,0,len);
				RpcCommunicator.instance().getLogger().debug("Got <<"+ new String(d,0,len));
				int first,last;
				first = strbuf.indexOf(RpcMessage.EnvelopBegin);
				last = strbuf.indexOf(RpcMessage.EnvelopClose);
				if(first == -1){
					if(last == -1){
						strbuf = ""; //闂佸搫鍟版慨闈涳耿娓氾拷鏋侀柛顐ゅ枔鍟搁梺璇″弾閸ㄨ鲸鎱ㄩ妶澶婃闁跨噦鎷�			
					}else{
						strbuf = strbuf.substring(last + RpcMessage.EnvelopClose.length());
					}
					continue;
				}else{
					if( first!=0){
						strbuf = strbuf.substring(first);
					}
					if(last == -1 ){
						if(strbuf.length() > RpcMessage.MAXPACKET_SIZE){ // 闂佸憡鐗曢幊鎾舵崲閸愨晛绶為柨鐕傛嫹						strbuf = "";
							_sock.close();
							RpcCommunicator.instance().getLogger().error("packet size too large! closesocket()");
						}
						continue;
					}
					// first and last okay,do parse
					String xml = strbuf.substring(0,last+RpcMessage.EnvelopClose.length());
					strbuf = strbuf.substring(last+RpcMessage.EnvelopClose.length());
					if(!decodeMsg(xml) ){
						//socket不关闭，仅仅提示
						//_sock.close();
						RpcCommunicator.instance().getLogger().error("decode message exception! ");
					}
				}// end fi				
			} // -- end while()
			
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error("connection lost!  detail:" + e.toString());
		}
		RpcCommunicator.instance().getLogger().debug("connection thread exiting...");
		onDisconnected();
	}
	
	@Override
	public boolean connect(){
		InetSocketAddress ep = new InetSocketAddress(_host,_port);
		try{
			_sock = new Socket();
			_sock.connect(ep,3000);
			_workthread = new Thread(this);
			_workthread.start();
			return true;
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error("<connect()>"+ e.toString());
		}
		_sock = null;
		return false;
	}
	
	@Override
	protected  void onDisconnected(){
		super.onDisconnected();
		_sock = null;
	}
	
	private boolean decodeMsg(String xml){
		RpcMessage m;
		m = RpcMessageXML.unmarshall(xml.getBytes());
		if(m!=null){
			m.conn = this;
			this.dispatchMsg(m);
			return true;
		}
		return false;
	}

	@Override
	public void close(){
		try{
			if( _sock == null){
				return;
			}
			_sock.close();
			_sock = null;
			if(_workthread !=null){
				_workthread.interrupt();
				_workthread.join();
				_workthread = null;
			}
			
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}
	}
	
	@Override
	protected
	synchronized boolean  sendDetail(RpcMessage m){
		try{
			if( _sock == null){
				if( !connect() ){
					m.errcode = tce.RpcConsts.RPCERROR_CONNECT_FAILED;
					return false;
				}
			}
			OutputStream os;
			os = _sock.getOutputStream();
			RpcMessageXML xml = (RpcMessageXML) m;
			byte[] bytes;
			bytes = xml.marshall();
			os.write(bytes);
		}catch(Exception e){
			m.errcode = tce.RpcConsts.RPCERROR_SENDFAILED;
			RpcCommunicator.instance().getLogger().error("<1.>"+e.toString());
			return false;
		}
		return true; // 必须始终返回false
	}
	
	@Override
	public  boolean sendMessage(RpcMessage m){
		return sendDetail(m);
	}
	
}
