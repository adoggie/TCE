

package tce;
import tce.mq.RpcConnection_QpidMQ;

import java.util.*;


public class RpcConnection implements Runnable{
	RpcAdapter _adapter = null;
	HashMap<Integer,RpcMessage> _msglist = new HashMap<Integer,RpcMessage>();
	protected String _host;
	protected int 	_port;
	protected int _type;
	protected boolean _connected = false;
	protected String _token = null;
	protected RpcConnectionAcceptor _acceptor = null;
	protected String  _name = "";
	protected boolean _ssl = false;


	RpcConnection(){

	}

	public String getName(){
		return _name;
	}

	public void setName(String name){
		_name = name;
	}

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

	public RpcAdapter getAdapter() {
		return _adapter;
	}

	public void setAdapter(RpcAdapter adapter) {
		this._adapter = adapter;
	}

	public RpcConnectionAcceptor getAcceptor(){
		return _acceptor;
	}

	public void setAcceptor(RpcConnectionAcceptor acceptor){
		_acceptor = acceptor;
	}

	public int getType(){
		return _type;
	}

	public boolean connect() {
		return false;
	}

	public boolean open(){
		return false;
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

//	public void attachAdapter(RpcAdapter adapter){
//		_adapter = adapter;
//		adapter.addConnection(this);
//	}

	public boolean isConnected(){
		return _connected;
	}

	void  onConnected(){
		_connected = true;
	}

	//clear up and free wait mutex for resuming user thread-control
	protected  void onDisconnected(){
		RpcCommunicator.instance().onConnectionDisconnected(this);
		_connected = false;
	}


	public  boolean sendMessage(RpcMessage m){
		//仅仅返回消息需要置入等待队列
		if( (m.calltype&RpcMessage.CALL)!=0 && (m.calltype&RpcMessage.ONEWAY) == 0 ){
			m.conn = this;
			RpcCommunicator.instance().enqueueMessage(m.sequence,m);
		}
		boolean r =  sendDetail(m);
		if(!r){
			if( (m.calltype&RpcMessage.CALL)!=0 && (m.calltype&RpcMessage.ONEWAY) == 0 ){
				RpcCommunicator.instance().dequeueMessage(m.sequence);
			}
		}
		return r;
	}

	protected boolean sendDetail(RpcMessage m){
		return false;
	}

	void doReturnMsg(RpcMessage m2){
		RpcMessage m1 = null;
		count+=1;

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

	static long count=0;

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

	protected void onMessage(RpcMessage m){
		if( _adapter == null &&  _acceptor!=null && _acceptor.getAdapter()!=null){
			_adapter = _acceptor.getAdapter();
		}
		if( _adapter!=null && _adapter.getDispatcher()!=null){
			_adapter.getDispatcher().dispatchMsg(m);
		}else{ // dispatch to global
			RpcCommunicator.instance().dispatchMsg(m);
		}
	}

	protected  boolean sendBytes(byte[] bytes){
		// should not be in here
		return false;
	}

}

