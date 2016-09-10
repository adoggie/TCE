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


public class ITerminalProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	public ITerminalProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ITerminalProxy create(String host,int port,Boolean ssl_enable){
		int type = RpcConsts.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConsts.CONNECTION_SSL;
		RpcConnection conn = RpcCommunicator.instance().createConnection(type,host,port);
		ITerminalProxy prx = new ITerminalProxy(conn);
		return prx;
	}	
	public static ITerminalProxy createWithProxy(RpcProxyBase proxy){
		ITerminalProxy prx = new ITerminalProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public void onMessage(String message) throws RpcException{
onMessage(message,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void onMessage(String message,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 3;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = message.getBytes();
			dos_4.writeInt(sb_5.length);
			dos_4.write(sb_5,0,sb_5.length);
			m_2.paramstream = bos_3.toByteArray();
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
	
	public void onMessage_oneway(String message,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 3;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = message.getBytes();
			dos_4.writeInt(sb_5.length);
			dos_4.write(sb_5,0,sb_5.length);
			m_2.paramstream = bos_3.toByteArray();
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void onMessage_async(String message,ITerminal_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		onMessage_async(message,async,props,null);
	}	
	
	public void onMessage_async(String message,ITerminal_AsyncCallBack async) throws RpcException{
		onMessage_async(message,async,null,null);
	}	
	
	public void onMessage_async(String message,ITerminal_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_6 = false;
		RpcMessage m_7 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_7.ifidx = 3;
		m_7.opidx = 0;
		m_7.paramsize = 1;
		m_7.extra.setProperties(props);
		m_7.cookie = cookie;
		try{
			ByteArrayOutputStream bos_8 = new ByteArrayOutputStream();
			DataOutputStream dos_9 = new DataOutputStream(bos_8);
			byte[] sb_10 = message.getBytes();
			dos_9.writeInt(sb_10.length);
			dos_9.write(sb_10,0,sb_10.length);
			m_7.paramstream = bos_8.toByteArray();
			m_7.prx = this;
			m_7.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_6 = this.conn.sendMessage(m_7);
		if(!r_6){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}
