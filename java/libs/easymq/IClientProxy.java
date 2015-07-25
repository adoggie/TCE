package easymq;
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


public class IClientProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	IClientProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static IClientProxy create(String host,int port){
		RpcConnection conn = RpcCommunicator.instance().createConnection(RpcConsts.CONNECTION_SOCK,host,port);
		IClientProxy prx = new IClientProxy(conn);
		return prx;
	}	
	public static IClientProxy createWithProxy(RpcProxyBase proxy){
		IClientProxy prx = new IClientProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public void onRecvData(mq_handle_t mq,message_t msg) throws RpcException{
onRecvData(mq,msg,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void onRecvData(mq_handle_t mq,message_t msg,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 0;
		m_2.opidx = 0;
		m_2.paramsize = 2;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			mq.marshall(dos_4);
			msg.marshall(dos_4);
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
	
	public void onRecvData_oneway(mq_handle_t mq,message_t msg,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 0;
		m_2.opidx = 0;
		m_2.paramsize = 2;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			mq.marshall(dos_4);
			msg.marshall(dos_4);
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
	
	public void onRecvData_async(mq_handle_t mq,message_t msg,IClient_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 0;
		m_6.opidx = 0;
		m_6.paramsize = 2;
		m_6.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_7 = new ByteArrayOutputStream();
			DataOutputStream dos_8 = new DataOutputStream(bos_7);
			mq.marshall(dos_8);
			msg.marshall(dos_8);
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
	
	
	
	public byte[] test(byte[] data,byte[] data2) throws RpcException{
		return test(data,data2,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public byte[] test(byte[] data,byte[] data2,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 0;
		m_2.opidx = 1;
		m_2.paramsize = 2;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			dos_4.writeInt(data.length);
			dos_4.write(data,0,data.length);
			dos_4.writeInt(data2.length);
			dos_4.write(data2,0,data2.length);
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
		byte[] b_5 = new byte[0];
		try{
			RpcMessage m2_6 = (RpcMessage) m_2.result;
			ByteBuffer d_7 = ByteBuffer.wrap(m2_6.paramstream);
			int _s_8 = d_7.getInt();
			b_5 = new byte[_s_8];
			d_7.get(b_5);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_5; //regardless if  unmarshalling is okay 
	}	
	
	public void test_async(byte[] data,byte[] data2,IClient_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_9 = false;
		RpcMessage m_10 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_10.ifidx = 0;
		m_10.opidx = 1;
		m_10.paramsize = 2;
		m_10.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_11 = new ByteArrayOutputStream();
			DataOutputStream dos_12 = new DataOutputStream(bos_11);
			dos_12.writeInt(data.length);
			dos_12.write(data,0,data.length);
			dos_12.writeInt(data2.length);
			dos_12.write(data2,0,data2.length);
			m_10.paramstream = bos_11.toByteArray();
			m_10.prx = this;
			m_10.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_9 = this.conn.sendMessage(m_10);
		if(!r_9){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}
