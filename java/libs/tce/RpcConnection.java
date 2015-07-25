

package tce;
import java.util.*;

import tce.RpcCommAdapter;
import tce.RpcCommunicator;
import tce.RpcMessage;
import tce.RpcConsts;


public class RpcConnection implements Runnable{
	RpcCommAdapter _adapter = null;
	HashMap<Integer,RpcMessage> _msglist = new HashMap<Integer,RpcMessage>();
	protected String _host;
	protected int 	_port;
	protected int _type;
	protected boolean _connected = false;

	protected String _token = null;


	public RpcConnection(String host,int port){
		_host = host;
		_port = port;
		_type = RpcConsts.CONNECTION_UNKNOWN;
	}

	// added 2013.11.25
	protected void setToken(String token){
		_token = token;
	}

	String getHost(){
		return _host;
	}

	int getPort(){
		return _port;
	}

	public RpcCommAdapter getAdapter() {
		return _adapter;
	}

	public void setAdapter(RpcCommAdapter adapter) {
		this._adapter = adapter;
		adapter.addConnection(this);

	}

	public int getType(){
		return _type;
	}

	public boolean connect() {
		return false;
	}

	public void open(){

	}

	public void close(){

	}

	@Override
	public void run(){

	}

	void onError(){

	}

	protected void join(){
		// pass
	}

	public void attachAdapter(RpcCommAdapter adapter){
		_adapter = adapter;
		adapter.addConnection(this);
	}

	public boolean isConnected(){
		return _connected;
	}

	void  onConnected(){
		_connected = true;
	}

	//clear up and free wait mutex for resuming user thread-control
	void onDisconnected(){
//		synchronized(this._msglist){
//			for( RpcMessage m: _msglist.values()){
//				try{
//					synchronized(m){
//						m.errcode = RpcConsts.RPCERROR_CONNECTION_LOST;
//						m.notify();
//					}
//				}catch(Exception e){
//					RpcCommunicator.instance().getLogger().error(
//							e.getMessage()
//							);
//				}
//			}
//			_msglist.clear();
//		}
		RpcCommunicator.instance().onConnectionDisconnected(this);
		_connected = false;
	}


	public  boolean sendMessage(RpcMessage m){
//		try{
//			Thread.sleep(100);
//		}catch(Exception e){}
		//仅仅返回消息需要置入等待队列
		if( (m.calltype&RpcMessage.CALL)!=0 && (m.calltype&RpcMessage.ONEWAY) == 0 ){
//				synchronized(this._msglist){
//					_msglist.put(m.sequence,m);
//				}
			m.conn = this;
			RpcCommunicator.instance().enqueueMessage(m.sequence,m);
		}
		boolean r =  sendDetail(m);
		if(!r){
			if( (m.calltype&RpcMessage.CALL)!=0 && (m.calltype&RpcMessage.ONEWAY) == 0 ){
//				synchronized(this._msglist){
//					_msglist.remove(m.sequence);
//				}
				RpcCommunicator.instance().dequeueMessage(m.sequence);
			}
		}
		return r;
	}

	protected
	boolean sendDetail(RpcMessage m){
		return false;
	}

	void doReturnMsg(RpcMessage m2){
		RpcMessage m1 = null;
		count+=1;

//		synchronized(this._msglist){
//			Integer key = new Integer(m2.sequence);
//
//			if( _msglist.containsKey(key) ){
//				m1 = _msglist.get(key);
//				_msglist.remove(key);
//			}
//		}
		m1 = RpcCommunicator.instance().dequeueMessage(m2.sequence);

		if(m1!=null){
			if(m1.async !=null){
				m1.async.callReturn(m1,m2); //闂佽瀛╅鏍窗閺嶎厼纾圭憸鐗堝俯閺佸棝鏌ｉ幇顒備粵閻庢凹鍓熼弻娑㈠箛閸忓摜鍑归梺鍝勬４閹凤拷		}else{
			}else{
				synchronized(m1){
					m1.result = m2; // assing to init-caller
					m1.notify();
				}
			}
		}
	}
//		else{
//			System.out.println("not matched..");
//		}
//	}

	static int count=0;

	protected void dispatchMsg(RpcMessage m){
		if( (m.calltype&RpcMessage.CALL) !=0){
			if(_adapter !=null){
				_adapter.dispatchMsg(m);
			}
		}
		if( (m.calltype&RpcMessage.RETURN)!=0){
			this.doReturnMsg(m);
		}
	}



}

