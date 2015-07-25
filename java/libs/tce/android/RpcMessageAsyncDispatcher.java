package tce.android;

//import java.util.Hashtable;
import java.util.*;
import android.os.Handler;
import android.os.Message;
import tce.RpcCommAdapter;
import tce.RpcCommunicator;
import tce.RpcConsts;
import tce.RpcMessage;
import tce.android.RpcAsyncCommThread;

//消息异步分派器
public class RpcMessageAsyncDispatcher{ //  implements Runnable{
	private static RpcMessageAsyncDispatcher _handle = null;
	Handler _uih = null;
	//RpcCommAdapter _adapter = null;
	Hashtable<Integer,RpcMessage> _msglist = new Hashtable<Integer,RpcMessage>();
	Vector<RpcCommAdapter> _adapters = new Vector<RpcCommAdapter>();

	RpcMessageAsyncDispatcher(){
		_uih = new Handler(){
			@Override
			public void handleMessage(Message msg) {
				//switch(msg.what){

				RpcMessage m =(RpcMessage) msg.obj; //接收到后台
				try{
					dispatchMsg(m);
				}catch(Exception e){
					RpcCommunicator.instance().getLogger().debug(e.toString());
					e.printStackTrace();
				}
			}
		};
	}

	void doReturnMsg(RpcMessage m2){
		RpcMessage m1 = null;
		synchronized(this._msglist){
			Integer key = Integer.valueOf(m2.sequence);

			if( _msglist.containsKey(key) ){
				m1 = _msglist.get(key);
				_msglist.remove(key);
			}
		}
		if(m1!=null){
			if(m1.async !=null){
				try{
					m1.async.callReturn(m1,m2);
				}catch(Exception e){
					RpcCommunicator.instance().getLogger().error("RpcMessageAsyncDispatcher.doReturnMsg: " + e.toString());
					e.printStackTrace();
				}
			}else{ //必须是异步
				RpcCommunicator.instance().getLogger().error("return Message is not async ,dropped!");
				/*
				synchronized(m1){
					m1.result = m2; // assing to init-caller
					m1.notify();
				}
				*/
			}
		}
	}

	//分派消息到应用代码
	void dispatchMsg(RpcMessage m){
		if(m.errcode == RpcConsts.RPCERROR_SENDFAILED){
			if(m.async != null){
				m.async.onError(m.errcode);
			}
			return;
		}
		if( (m.calltype&RpcMessage.CALL) !=0){
			if(m.conn.getAdapter() !=null){
				m.conn.getAdapter().dispatchMsg(m);
			}
		}
		if( (m.calltype&RpcMessage.RETURN)!=0){
			this.doReturnMsg(m);
		}
	}

	public Handler getHandler(){
		return _uih;
	}

	public final static RpcMessageAsyncDispatcher instance(){
		if(_handle == null){
			_handle = new RpcMessageAsyncDispatcher();
		}
		return _handle;
	}

	public final boolean sendMessage(RpcMessage m){
		synchronized(this._msglist){
			if( (m.calltype & RpcMessage.CALL) != 0 ){
				if( (m.calltype & RpcMessage.ASYNC) !=0 ){
					_msglist.put(m.sequence,m);
				}
			}

		}

		Message msg = new Message();
		msg.what = RpcConsts.ASYNC_RPCMSG;
		msg.obj = m;
		RpcAsyncCommThread.instance().getHandler().sendMessage(msg);

		return true;
	}

	public void close(){

	}
}
