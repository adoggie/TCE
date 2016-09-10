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


public class ITerminalGatewayServerProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	public ITerminalGatewayServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ITerminalGatewayServerProxy create(String host,int port,Boolean ssl_enable){
		int type = RpcConsts.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConsts.CONNECTION_SSL;
		RpcConnection conn = RpcCommunicator.instance().createConnection(type,host,port);
		ITerminalGatewayServerProxy prx = new ITerminalGatewayServerProxy(conn);
		return prx;
	}	
	public static ITerminalGatewayServerProxy createWithProxy(RpcProxyBase proxy){
		ITerminalGatewayServerProxy prx = new ITerminalGatewayServerProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public void ping() throws RpcException{
ping(tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void ping(int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
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
	}	
	
	public void ping_oneway(HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 1;
		m_2.opidx = 0;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		ping_async(async,props,null);
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async) throws RpcException{
		ping_async(async,null,null);
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_3 = false;
		RpcMessage m_4 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_4.ifidx = 1;
		m_4.opidx = 0;
		m_4.paramsize = 0;
		m_4.extra.setProperties(props);
		m_4.cookie = cookie;
		try{
			m_4.prx = this;
			m_4.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_3 = this.conn.sendMessage(m_4);
		if(!r_3){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}
