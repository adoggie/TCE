package tce;

import java.util.*;

import tce.RpcServant;
import tce.RpcServantDelegate;
import tce.RpcMessage;
import tce.RpcMessageXML;

public class RpcCommAdapterXML extends RpcCommAdapter {
	Hashtable<String,RpcServantDelegate> _servants = new 
			Hashtable<String,RpcServantDelegate>();
	
	public RpcCommAdapterXML(String _id){
		super(_id);
	}
	
	@Override
	boolean open(String host,int port){
		return false;
	}
	
	@Override
	public void  addServant(RpcServant servant){
		_servants.put(servant.delegate.index, servant.delegate);
	}
	
	
	@Override
	public void dispatchMsg(RpcMessage m){
		//RpcConnection conn = m.conn;
		RpcMessageXML xml = (RpcMessageXML)m;
		RpcServantDelegate dg = null;
		if( (xml.calltype & RpcMessage.CALL) != 0 ){
			
			synchronized (_servants){
				if(! _servants.containsKey(xml.msgcls ) ){ // found by function-name
					doError(RpcConsts.RPCERROR_INTERFACE_NOTFOUND,m);
					return;
				}
				dg = _servants.get(xml.msgcls);
				//_servants.remove(xml.msg);
			}
			if( dg == null){
				return;
			}
			
			
			dg.invoke(m);
			
			
		}
	}
}
