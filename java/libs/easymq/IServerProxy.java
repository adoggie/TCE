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


public class IServerProxy extends RpcProxyBase{
	//# -- INTERFACE PROXY -- 
	
	IServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static IServerProxy create(String host,int port){
		RpcConnection conn = RpcCommunicator.instance().createConnection(RpcConsts.CONNECTION_SOCK,host,port);
		IServerProxy prx = new IServerProxy(conn);
		return prx;
	}	
	public static IServerProxy createWithProxy(RpcProxyBase proxy){
		IServerProxy prx = new IServerProxy(proxy.conn);
		return prx;
	}	
	
	public void destroy(){
		try{
			conn.close();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.getMessage());
		}		
	}	
	
	public String register(String user) throws RpcException{
		return register(user,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public String register(String user,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = user.getBytes();
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
			int _sb_9 = d_8.getInt();
			byte[] _sb_10 = new byte[_sb_9];
			d_8.get(_sb_10);
			b_6 = new String(_sb_10);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_6; //regardless if  unmarshalling is okay 
	}	
	
	public void register_async(String user,IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_11 = false;
		RpcMessage m_12 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_12.ifidx = 1;
		m_12.opidx = 0;
		m_12.paramsize = 1;
		m_12.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_13 = new ByteArrayOutputStream();
			DataOutputStream dos_14 = new DataOutputStream(bos_13);
			byte[] sb_15 = user.getBytes();
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
	
	
	
	public void heartbeat() throws RpcException{
heartbeat(tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void heartbeat(int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 1;
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
	
	public void heartbeat_oneway(HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 1;
		m_2.opidx = 1;
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
	
	public void heartbeat_async(IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_3 = false;
		RpcMessage m_4 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_4.ifidx = 1;
		m_4.opidx = 1;
		m_4.paramsize = 0;
		m_4.extra.setProperties(props);
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
	
	
	
	public mq_handle_t openMQ(String name,Integer type,Integer flags,Integer mode) throws RpcException{
		return openMQ(name,type,flags,mode,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public mq_handle_t openMQ(String name,Integer type,Integer flags,Integer mode,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 2;
		m_2.paramsize = 4;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			byte[] sb_5 = name.getBytes();
			dos_4.writeInt(sb_5.length);
			dos_4.write(sb_5,0,sb_5.length);
			dos_4.writeInt(type);
			dos_4.writeInt(flags);
			dos_4.writeInt(mode);
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
		mq_handle_t b_6 = new mq_handle_t();
		try{
			RpcMessage m2_7 = (RpcMessage) m_2.result;
			ByteBuffer d_8 = ByteBuffer.wrap(m2_7.paramstream);
			r_1 = b_6.unmarshall(d_8);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_6; //regardless if  unmarshalling is okay 
	}	
	
	public void openMQ_async(String name,Integer type,Integer flags,Integer mode,IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_9 = false;
		RpcMessage m_10 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_10.ifidx = 1;
		m_10.opidx = 2;
		m_10.paramsize = 4;
		m_10.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_11 = new ByteArrayOutputStream();
			DataOutputStream dos_12 = new DataOutputStream(bos_11);
			byte[] sb_13 = name.getBytes();
			dos_12.writeInt(sb_13.length);
			dos_12.write(sb_13,0,sb_13.length);
			dos_12.writeInt(type);
			dos_12.writeInt(flags);
			dos_12.writeInt(mode);
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
	
	
	
	public void closeMQ(mq_handle_t mq) throws RpcException{
closeMQ(mq,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void closeMQ(mq_handle_t mq,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 3;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			mq.marshall(dos_4);
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
	
	public void closeMQ_oneway(mq_handle_t mq,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 1;
		m_2.opidx = 3;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_3 = new ByteArrayOutputStream();
			DataOutputStream dos_4 = new DataOutputStream(bos_3);
			mq.marshall(dos_4);
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
	
	public void closeMQ_async(mq_handle_t mq,IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 1;
		m_6.opidx = 3;
		m_6.paramsize = 1;
		m_6.extra.setProperties(props);
		try{
			ByteArrayOutputStream bos_7 = new ByteArrayOutputStream();
			DataOutputStream dos_8 = new DataOutputStream(bos_7);
			mq.marshall(dos_8);
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
	
	
	
	public void writeMQ(mq_handle_t mq,message_t msg) throws RpcException{
writeMQ(mq,msg,tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void writeMQ(mq_handle_t mq,message_t msg,int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 4;
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
	
	public void writeMQ_oneway(mq_handle_t mq,message_t msg,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 1;
		m_2.opidx = 4;
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
	
	public void writeMQ_async(mq_handle_t mq,message_t msg,IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 1;
		m_6.opidx = 4;
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
	
	
	
	public Vector<mq_info_t> getMqStaticstic() throws RpcException{
		return getMqStaticstic(tce.RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public Vector<mq_info_t> getMqStaticstic(int timeout,HashMap<String,String> props) throws RpcException{
		boolean r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 5;
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
		Vector<mq_info_t> b_3 = new Vector<mq_info_t>();
		try{
			RpcMessage m2_4 = (RpcMessage) m_2.result;
			ByteBuffer d_5 = ByteBuffer.wrap(m2_4.paramstream);
			mq_info_list_thlp ar_6 = new mq_info_list_thlp(b_3);
			r_1 = ar_6.unmarshall(d_5);
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY);
		}		
		return b_3; //regardless if  unmarshalling is okay 
	}	
	
	public void getMqStaticstic_async(IServer_AsyncCallBack async,HashMap<String,String> props) throws RpcException{
		boolean r_7 = false;
		RpcMessage m_8 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_8.ifidx = 1;
		m_8.opidx = 5;
		m_8.paramsize = 0;
		m_8.extra.setProperties(props);
		try{
			m_8.prx = this;
			m_8.async = async;
		}catch(Exception e){
			throw new RpcException(RpcConsts.RPCERROR_DATADIRTY,e.toString());
		}		
		r_7 = this.conn.sendMessage(m_8);
		if(!r_7){
			throw new RpcException(RpcConsts.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}
