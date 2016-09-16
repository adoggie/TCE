package tce;

import java.util.*;

public class RpcAdapterXML extends RpcAdapter {
	Hashtable<String,RpcServantDelegate> _servants = new 
			Hashtable<String,RpcServantDelegate>();
	
	public RpcAdapterXML(String _id){
		super(_id);
	}
	
	@Override
	public boolean open(){
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
			
			try {
				dg.invoke(m);
			}catch (Exception e){
				RpcCommunicator.instance().getLogger().error(e.toString());
			}
			
			
		}
	}
}
