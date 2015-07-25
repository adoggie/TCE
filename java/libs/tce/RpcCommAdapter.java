
/*
 * adapter 闁稿﹦鍠庢慨鐚歰nnection閻庡湱鍋熼獮鍥р槈閸喍绱栭柛娆愬灴閿熶粙宕仦鎯у闁猴拷鎷�* xml闁汇劌澧攑c闁革负鍔忕换娑㈠箳閵夈倗鐟愰柛娆樹簻閸樻垹鎷嬮梹鎰伇濞戞挾瀵磀apter閻庢稒锚濠�拷 * 闁兼澘鐣甦apter闁告瑯鍨禍鎺楀礂娴ｇ瓔鍟呭鑸电煯闁叉竷onnnection
 * */

package tce;


import java.util.*;

import tce.RpcServant;
import tce.RpcServantDelegate;
import tce.RpcMessage;
//import tce.RpcMessageXML;

public class RpcCommAdapter{
	String _id;
	
	Hashtable<Integer,RpcServantDelegate> _servants = new 
			Hashtable<Integer,RpcServantDelegate>();
	
	Vector<RpcConnection> _conns = new Vector<RpcConnection>();
	
	public RpcCommAdapter(String id){
		_id = id;
	}
	
	public String get_id() {
		return _id;
	}

	public void set_id(String _id) {
		this._id = _id;
	}

	boolean open(String host,int port){
		return false;
	}
	
	public void  addServant(RpcServant servant){
		_servants.put(servant.delegate.ifidx, servant.delegate);
	}
	
	public void addConnection(RpcConnection conn){
		for(RpcConnection e:_conns){
			if( e == conn){
				return ;
			}
		}
		_conns.add(conn);
	}
	
	void doError(int errcode,RpcMessage m){
//		RpcConnection conn = m.conn;
		/*
		var sm:RpcMessageReturn = new RpcMessageReturn();
		sm.sequence = m.sequence;
		sm.errcode = errcode;
		conn.sendMessage(sm);
		*/
	}
	
	void close(){
		
	}
	
	protected void join(){
		for(RpcConnection e:_conns){
			e.join();
		}
	}
	
	public void dispatchMsg(RpcMessage m){
		RpcServantDelegate dg = null;
		if( (m.calltype & RpcMessage.CALL) != 0 ){
			synchronized (_servants){
				if(! _servants.containsKey( m.ifidx) ){ // found by function-name
					doError(RpcConsts.RPCERROR_INTERFACE_NOTFOUND,m);
					return;
				}
				dg = _servants.get(m.ifidx);
			}
			if( dg == null){
				return;
			}
			dg.invoke(m);
		}
	}
	
}

