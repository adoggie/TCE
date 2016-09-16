
/*
 * adapter 闁稿﹦鍠庢慨鐚歰nnection閻庡湱鍋熼獮鍥р槈閸喍绱栭柛娆愬灴閿熶粙宕仦鎯у闁猴拷鎷�* xml闁汇劌澧攑c闁革负鍔忕换娑㈠箳閵夈倗鐟愰柛娆樹簻閸樻垹鎷嬮梹鎰伇濞戞挾瀵磀apter閻庢稒锚濠�拷 * 闁兼澘鐣甦apter闁告瑯鍨禍鎺楀礂娴ｇ瓔鍟呭鑸电煯闁叉竷onnnection
 * */

package tce;


import java.util.*;

import tce.RpcServant;
import tce.RpcServantDelegate;
import tce.RpcMessage;
//import tce.RpcMessageXML;

public class RpcAdapter implements RpcMessageDispatcher.Client {

	public class Settings{
		public int threadNum = 0;
	}

	String _id;
	Hashtable<Integer,RpcServantDelegate> _servants = new 
			Hashtable<Integer,RpcServantDelegate>();
	Vector<RpcConnection> _conns = new Vector<RpcConnection>();
	Vector<RpcConnectionAcceptor> _acceptors = new Vector<RpcConnectionAcceptor>();
	Settings _settings = new Settings();
	RpcMessageDispatcher _dispatcher ;


	public Settings getSettings(){
		return _settings;
	}

	public RpcAdapter(String id){
		_id = id;
	}
	
	public String getID() {
		return _id;
	}

	public void setID(String _id) {
		this._id = _id;
	}

	RpcMessageDispatcher getDispatcher(){
		return _dispatcher;
	}

	public String getName(){
		return getID();
	}

	public boolean open(){
		boolean succ = false;
		if( getSettings().threadNum > 0){
			_dispatcher = new RpcMessageDispatcher(this,getSettings().threadNum);
			succ = _dispatcher.open();
		}

		synchronized (_acceptors){
			for(RpcConnectionAcceptor acceptor : _acceptors){
				if( acceptor.isOpen() == false){
					if( !acceptor.open()){
						RpcCommunicator.instance().getLogger().error("open connection acceptor failed!");
					}
				}
			}
		}
		return succ ;
	}


	public void  addServant(RpcServant servant){
		_servants.put(servant.delegate.ifidx, servant.delegate);
	}
	
	public synchronized void attachConnection(RpcConnection conn){
		if (!_conns.contains(conn) ){
			_conns.add(conn);
			conn.setAdapter(this);
		}
	}

	public synchronized void detachConnection(RpcConnection conn){
		if( _conns.contains(conn)){
			_conns.remove(conn);
			conn.setAdapter(null);
		}
	}

	void doError(int errcode,RpcMessage m){
		RpcMessageReturn msgreturn = new RpcMessageReturn(m.sequence,errcode);
		msgreturn.send(m.conn);
	}

	public synchronized void addConnectionAcceptor(RpcConnectionAcceptor acceptor){
		if(!_acceptors.contains(acceptor)){
			_acceptors.add(acceptor);
			acceptor.setAdapter(this);
		}
	}


	public synchronized void removeConnectionAcceptor(RpcConnectionAcceptor acceptor){
		_acceptors.remove( acceptor);
		acceptor.setAdapter(null);
	}
	
	public void close(){
		
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
			try {
				RpcMessage msgreturn = dg.invoke(m);
				if( msgreturn != null){
					m.conn.sendMessage(msgreturn);
				}
			} catch(Exception e){
				RpcCommunicator.instance().getLogger().error(" execute servant failed:" + e.toString());
				doError(RpcConsts.RPCERROR_REMOTEMETHOD_EXCEPTION,m);
			}
		}
	}
	
}

