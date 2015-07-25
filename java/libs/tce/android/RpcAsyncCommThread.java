package tce.android;

//import java.util.Hashtable;
import android.os.Handler;
import android.os.Message;
import android.os.Looper;
//import android.net.LocalSocket;
import android.util.Log;

import tce.RpcMessage;
import tce.android.RpcMessageAsyncDispatcher;

import tce.RpcConsts;
//RpcAsyncCommThread
//锟届步通锟斤拷锟竭筹拷 锟斤拷 锟斤拷锟酵和斤拷锟斤拷rpc锟斤拷息锟斤拷锟斤拷android锟斤拷锟斤拷锟竭筹拷锟斤拷锟斤拷锟较拷锟斤拷蟹锟绞斤拷慕锟斤拷锟�
public class RpcAsyncCommThread  implements Runnable{

	private static RpcAsyncCommThread _handle = null;
	private Handler _uih = null;
	//private Handler _loch= null; //锟斤拷锟斤拷锟斤拷息锟斤拷锟秸达拷锟斤拷锟斤拷
	private Thread _thread = null;
//	public RpcAsyncCommThread setUiHandler(Handler h){
//		_uih = h;
//		return this;
//	}

	public RpcAsyncCommThread(){
		_thread = new Thread(this);
		_thread.start();
	}

	public Handler getHandler(){
		return _uih;
	}

	public void close(){

	}

	//锟斤拷锟斤拷ui锟竭程达拷锟捷癸拷锟斤拷锟斤拷息
	//@Override
	public void run(){
		 Looper.prepare();
		_uih = new Handler(){
			//锟斤拷取锟斤拷锟斤拷锟斤拷锟斤拷
			@Override
			public void handleMessage(Message msg) {
				System.out.println("AsyncCommThread got one message. ready to send out..");
				RpcMessage m =(RpcMessage) msg.obj;
				boolean r;
				r = m.prx.conn.sendMessage(m);
				if(r == false){
					//throw errmsg back
					//RpcMessageAsyncDispatcher.instance().getHandler().sendMessage(m); //m锟窖撅拷携锟斤拷锟斤拷锟斤拷锟�
					m.calltype = RpcMessage.RETURN;
					m.errcode = RpcConsts.RPCERROR_SENDFAILED; // send failed
					dispatchMsg(m);
				}
			}
		};
		Looper.loop();
	}

	public static  RpcAsyncCommThread instance(){
		if(_handle == null){
			_handle = new RpcAsyncCommThread();
		}
		return _handle;

	}

	//投锟捷碉拷锟斤拷锟斤拷锟竭筹拷
	public void dispatchMsg(RpcMessage m){
		// m.delta -

		Message msg = new Message();
		msg.what = RpcConsts.ASYNC_RPCMSG;
		msg.obj = m;

		RpcMessageAsyncDispatcher.instance().getHandler().sendMessage(msg);
	}
}
