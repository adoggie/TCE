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


public class ServerProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	public ServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ServerProxy create(String host,int port,Boolean ssl_enable){
		int type = RpcConsts.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConsts.CONNECTION_SSL;
		RpcConnection conn = RpcCommunicator.instance().createConnection(type,host,port);
		ServerProxy prx = new ServerProxy(conn);
		return prx;
	}	
	public static ServerProxy createWithProxy(RpcProxyBase proxy){
		ServerProxy prx = new ServerProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public String echo(String text) throws RpcException{
		return echo(text,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public String echo(String text,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = text.getBytes();
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
		String b_6 = "";
		try{
			RpcMessage m2_7 = (RpcMessage) m_2.result;
			ByteBuffer d_8 = ByteBuffer.wrap(m2_7.paramstream);
			int v_9 = d_8.getInt();
			byte[] _sb_10 = new byte[v_9];
			d_8.get(_sb_10);
			b_6 = new String(_sb_10);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_6; //regardless if  unmarshalling is okay 
	}	
	
	public void echo_async(String text,Server_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		echo_async(text,async,props,null);
	}	
	
	public void echo_async(String text,Server_AsyncCallBack async) throws RpcException{
		echo_async(text,async,null,null);
	}	
	
	public void echo_async(String text,Server_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_11 = false;
		RpcMessage m_12 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_12.ifidx = 2;
		m_12.opidx = 0;
		m_12.paramsize = 1;
		m_12.extra.setProperties(props);
		m_12.cookie = cookie;
		try{
			ByteArrayOutputStream bos_13 = new ByteArrayOutputStream();
			DataOutputStream dos_14 = new DataOutputStream(bos_13);
			byte[] sb_15 = text.getBytes();
			dos_14.writeInt(sb_15.length);
			dos_14.write(sb_15,0,sb_15.length);
			m_12.paramstream = bos_13.toByteArray();
			m_12.prx = this;
			m_12.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_11 = this.conn.sendMessage(m_12);
		if(!r_11){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
	
	public void timeout(Integer secs) throws RpcException{
timeout(secs,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void timeout(Integer secs,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 1;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			dos_4.writeInt(secs);
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
	
	public void timeout_oneway(Integer secs,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 1;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			dos_4.writeInt(secs);
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
	
	public void timeout_async(Integer secs,Server_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		timeout_async(secs,async,props,null);
	}	
	
	public void timeout_async(Integer secs,Server_AsyncCallBack async) throws RpcException{
		timeout_async(secs,async,null,null);
	}	
	
	public void timeout_async(Integer secs,Server_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 2;
		m_6.opidx = 1;
		m_6.paramsize = 1;
		m_6.extra.setProperties(props);
		m_6.cookie = cookie;
		try{
			ByteArrayOutputStream bos_7 = new ByteArrayOutputStream();
			DataOutputStream dos_8 = new DataOutputStream(bos_7);
			dos_8.writeInt(secs);
			m_6.paramstream = bos_7.toByteArray();
			m_6.prx = this;
			m_6.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_5 = this.conn.sendMessage(m_6);
		if(!r_5){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
	
	public void heartbeat(String hello) throws RpcException{
heartbeat(hello,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void heartbeat(String hello,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 2;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = hello.getBytes();
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
	
	public void heartbeat_oneway(String hello,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 2;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = hello.getBytes();
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
	
	public void heartbeat_async(String hello,Server_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		heartbeat_async(hello,async,props,null);
	}	
	
	public void heartbeat_async(String hello,Server_AsyncCallBack async) throws RpcException{
		heartbeat_async(hello,async,null,null);
	}	
	
	public void heartbeat_async(String hello,Server_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_6 = false;
		RpcMessage m_7 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_7.ifidx = 2;
		m_7.opidx = 2;
		m_7.paramsize = 1;
		m_7.extra.setProperties(props);
		m_7.cookie = cookie;
		try{
			ByteArrayOutputStream bos_8 = new ByteArrayOutputStream();
			DataOutputStream dos_9 = new DataOutputStream(bos_8);
			byte[] sb_10 = hello.getBytes();
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
	
	
	
	public void bidirection() throws RpcException{
bidirection(tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void bidirection(int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 3;
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
	
	public void bidirection_oneway(HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 3;
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
	
	public void bidirection_async(Server_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		bidirection_async(async,props,null);
	}	
	
	public void bidirection_async(Server_AsyncCallBack async) throws RpcException{
		bidirection_async(async,null,null);
	}	
	
	public void bidirection_async(Server_AsyncCallBack async,HashMap<String,String> props,Object cookie) throws RpcException{
		boolean r_3 = false;
		RpcMessage m_4 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_4.ifidx = 2;
		m_4.opidx = 3;
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
