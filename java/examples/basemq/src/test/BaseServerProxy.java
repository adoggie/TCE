package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	

import tce.*;
import java.io.*;
import java.nio.*;
import java.util.*;


public class BaseServerProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	public BaseServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static BaseServerProxy create(String host,int port,Boolean ssl_enable){
		int type = RpcConsts.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConsts.CONNECTION_SSL;
		RpcConnection conn = RpcCommunicator.instance().createConnection(type,host,port);
		BaseServerProxy prx = new BaseServerProxy(conn);
		return prx;
	}	
	public static BaseServerProxy createWithProxy(RpcProxyBase proxy){
		BaseServerProxy prx = new BaseServerProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public String datetime() throws RpcException{
		return datetime(tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public String datetime(int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 0;
		m_2.opidx = 0;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		synchronized(m_2){
			r_1 = this.conn.sendMessage(m_2);
			if(!r_1){
				throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
			}			
			try{
				if( timeout > 0) m_2.wait(timeout);
				else m_2.wait();
			}catch(Exception e){
				throw new RpcException(RpcConsts.RPCERROR_INTERNAL_EXCEPTION,e.getMessage());
			}			
		}		
		if (m_2.errcode != RpcConsts.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcConsts.RPCERROR_TIMEOUT);
		}		
		String b_3 = "";
		try{
			RpcMessage m2_4 = (RpcMessage) m_2.result;
			ByteBuffer d_5 = ByteBuffer.wrap(m2_4.paramstream);
			int v_6 = d_5.getInt();
			byte[] _sb_7 = new byte[v_6];
			d_5.get(_sb_7);
			b_3 = new String(_sb_7);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_3; //regardless if  unmarshalling is okay 
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		datetime_async(async,props,null);
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async) throws RpcException{
		datetime_async(async,null,null);
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_8 = false;
		RpcMessage m_9 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_9.ifidx = 0;
		m_9.opidx = 0;
		m_9.paramsize = 0;
		m_9.extra.setProperties(props);
		m_9.cookie = cookie;
		try{
			m_9.prx = this;
			m_9.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_8 = this.conn.sendMessage(m_9);
		if(!r_8){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}
