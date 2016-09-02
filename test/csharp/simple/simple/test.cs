
/*
#---------------------------------
#  - TCE -
#  Tiny Communication Engine (Csharp version)
#
#  sw2us.com copyright @2016
#  bin.zhang@sw2us.com / qq:24509826
#---------------------------------
*/


using System;
using Tce;
using System.Collections.Generic;
using System.IO;
using System.Net;

namespace test{
	

public class BaseServerProxy:RpcProxyBase{
	//-- interface proxy -- 
	
	public BaseServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static BaseServerProxy create(string host,int port,bool ssl_enable){
		int type = RpcConstValue.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConstValue.CONNECTION_SSL;
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
			RpcCommunicator.instance().getLogger().error(e.ToString());
		}		
	}	
	
	public string datetime(){
		return datetime(RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public string datetime(int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 0;
		m_2.opidx = 0;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_3 = false;
		try{
			if( timeout > 0) _rc_3 = m_2.ev.WaitOne(timeout);
			else _rc_3 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_3 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
		string b_4 = "";
		try{
			RpcMessage m2_5 = (RpcMessage) m_2.result;
			MemoryStream d_6 = new MemoryStream(m2_5.paramstream);
			BinaryReader _reader_7 = new BinaryReader(d_6);
			b_4 = RpcBinarySerializer.readString(_reader_7);
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY);
		}		
		return b_4; //regardless if  unmarshalling is okay 
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async,Dictionary<string,string> props){
		datetime_async(async,props,null);
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async){
		datetime_async(async,null,null);
	}	
	
	public void datetime_async(BaseServer_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_8 = false;
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
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_8 = this.conn.sendMessage(m_9);
		if(!r_8){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}


public class BaseServer_AsyncCallBack: RpcAsyncCallBackBase{
	// following functions should be overrided in user code.
	public void datetime(string result,RpcProxyBase proxy,object cookie){
	}	
	
	public override void callReturn(RpcMessage m1,RpcMessage m2){
		bool r = false;
		MemoryStream d = new MemoryStream(m2.paramstream);
		BinaryReader reader = new BinaryReader(d);
		if( m1.opidx == 0 ){
			string b_10 = "";
			b_10 = RpcBinarySerializer.readString(reader);
			datetime(b_10,m1.prx,m1.cookie);
		}		
	}	
}

public class BaseServer : RpcServant{
	//# -- INTERFACE -- 
	public BaseServer(){
		this.delegate_ = new BaseServer_delegate(this);
	}	
	
	
	public virtual string datetime(RpcContext ctx){
		return "";
	}	
}

public class BaseServer_delegate : RpcServantDelegate {
	
	BaseServer inst = null;
	public BaseServer_delegate(BaseServer inst){
		this.ifidx = 0;
		this.inst = inst;
	}	
	
	public override bool invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: datetime
	bool func_0_delegate(RpcMessage m){
		bool r = false;
		BaseServer servant = (BaseServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		string cr;
		cr = servant.datetime(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		mr.conn = m.conn;
		mr.ifidx = m.ifidx;
		mr.call_id = m.call_id;
		if(m.extra.getProperties().ContainsKey("__user_id__")){
			mr.extra.setPropertyValue("__user_id__",m.extra.getPropertyValue("__user_id__"));
		}		
		try{
			MemoryStream _bos_11 = new MemoryStream();
			BinaryWriter dos = new BinaryWriter(_bos_11);
			RpcBinarySerializer.writeString(cr,dos);
			mr.paramsize = 1;
			mr.paramstream = _bos_11.ToArray();
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	
	
}


public class ITerminalGatewayServerProxy:RpcProxyBase{
	//-- interface proxy -- 
	
	public ITerminalGatewayServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ITerminalGatewayServerProxy create(string host,int port,bool ssl_enable){
		int type = RpcConstValue.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConstValue.CONNECTION_SSL;
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
			RpcCommunicator.instance().getLogger().error(e.ToString());
		}		
	}	
	
	public void ping(){
ping(RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void ping(int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 1;
		m_2.opidx = 0;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_3 = false;
		try{
			if( timeout > 0) _rc_3 = m_2.ev.WaitOne(timeout);
			else _rc_3 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_3 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
	}	
	
	public void ping_oneway(Dictionary<string,string> props){
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 1;
		m_2.opidx = 0;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async,Dictionary<string,string> props){
		ping_async(async,props,null);
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async){
		ping_async(async,null,null);
	}	
	
	public void ping_async(ITerminalGatewayServer_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_3 = false;
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
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_3 = this.conn.sendMessage(m_4);
		if(!r_3){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}


public class ITerminalGatewayServer_AsyncCallBack: RpcAsyncCallBackBase{
	// following functions should be overrided in user code.
	public void ping(RpcProxyBase proxy,object cookie){
	}	
	
	public override void callReturn(RpcMessage m1,RpcMessage m2){
		bool r = false;
		MemoryStream d = new MemoryStream(m2.paramstream);
		BinaryReader reader = new BinaryReader(d);
		if( m1.opidx == 0 ){
			ping(m1.prx,m1.cookie);
		}		
	}	
}

public class ITerminalGatewayServer : RpcServant{
	//# -- INTERFACE -- 
	public ITerminalGatewayServer(){
		this.delegate_ = new ITerminalGatewayServer_delegate(this);
	}	
	
	
	public virtual void ping(RpcContext ctx){
	}	
}

public class ITerminalGatewayServer_delegate : RpcServantDelegate {
	
	ITerminalGatewayServer inst = null;
	public ITerminalGatewayServer_delegate(ITerminalGatewayServer inst){
		this.ifidx = 1;
		this.inst = inst;
	}	
	
	public override bool invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: ping
	bool func_0_delegate(RpcMessage m){
		bool r = false;
		ITerminalGatewayServer servant = (ITerminalGatewayServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.ping(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}


public class ServerProxy:RpcProxyBase{
	//-- interface proxy -- 
	
	public ServerProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ServerProxy create(string host,int port,bool ssl_enable){
		int type = RpcConstValue.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConstValue.CONNECTION_SSL;
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
			RpcCommunicator.instance().getLogger().error(e.ToString());
		}		
	}	
	
	public string echo(string text){
		return echo(text,RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public string echo(string text,int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeString(text,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_5 = false;
		try{
			if( timeout > 0) _rc_5 = m_2.ev.WaitOne(timeout);
			else _rc_5 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_5 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
		string b_6 = "";
		try{
			RpcMessage m2_7 = (RpcMessage) m_2.result;
			MemoryStream d_8 = new MemoryStream(m2_7.paramstream);
			BinaryReader _reader_9 = new BinaryReader(d_8);
			b_6 = RpcBinarySerializer.readString(_reader_9);
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY);
		}		
		return b_6; //regardless if  unmarshalling is okay 
	}	
	
	public void echo_async(string text,Server_AsyncCallBack async,Dictionary<string,string> props){
		echo_async(text,async,props,null);
	}	
	
	public void echo_async(string text,Server_AsyncCallBack async){
		echo_async(text,async,null,null);
	}	
	
	public void echo_async(string text,Server_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_10 = false;
		RpcMessage m_11 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_11.ifidx = 2;
		m_11.opidx = 0;
		m_11.paramsize = 1;
		m_11.extra.setProperties(props);
		m_11.cookie = cookie;
		try{
			MemoryStream bos_12 = new MemoryStream();
			BinaryWriter dos_13 = new BinaryWriter(bos_12);
			RpcBinarySerializer.writeString(text,dos_13);
			m_11.paramstream = bos_12.ToArray();
			m_11.prx = this;
			m_11.async = async;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_10 = this.conn.sendMessage(m_11);
		if(!r_10){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
	
	public void timeout(int secs){
timeout(secs,RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void timeout(int secs,int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 1;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeInt(secs,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_5 = false;
		try{
			if( timeout > 0) _rc_5 = m_2.ev.WaitOne(timeout);
			else _rc_5 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_5 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
	}	
	
	public void timeout_oneway(int secs,Dictionary<string,string> props){
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 1;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeInt(secs,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void timeout_async(int secs,Server_AsyncCallBack async,Dictionary<string,string> props){
		timeout_async(secs,async,props,null);
	}	
	
	public void timeout_async(int secs,Server_AsyncCallBack async){
		timeout_async(secs,async,null,null);
	}	
	
	public void timeout_async(int secs,Server_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 2;
		m_6.opidx = 1;
		m_6.paramsize = 1;
		m_6.extra.setProperties(props);
		m_6.cookie = cookie;
		try{
			MemoryStream bos_7 = new MemoryStream();
			BinaryWriter dos_8 = new BinaryWriter(bos_7);
			RpcBinarySerializer.writeInt(secs,dos_8);
			m_6.paramstream = bos_7.ToArray();
			m_6.prx = this;
			m_6.async = async;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_5 = this.conn.sendMessage(m_6);
		if(!r_5){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
	
	public void heartbeat(string hello){
heartbeat(hello,RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void heartbeat(string hello,int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 2;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeString(hello,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_5 = false;
		try{
			if( timeout > 0) _rc_5 = m_2.ev.WaitOne(timeout);
			else _rc_5 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_5 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
	}	
	
	public void heartbeat_oneway(string hello,Dictionary<string,string> props){
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 2;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeString(hello,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void heartbeat_async(string hello,Server_AsyncCallBack async,Dictionary<string,string> props){
		heartbeat_async(hello,async,props,null);
	}	
	
	public void heartbeat_async(string hello,Server_AsyncCallBack async){
		heartbeat_async(hello,async,null,null);
	}	
	
	public void heartbeat_async(string hello,Server_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 2;
		m_6.opidx = 2;
		m_6.paramsize = 1;
		m_6.extra.setProperties(props);
		m_6.cookie = cookie;
		try{
			MemoryStream bos_7 = new MemoryStream();
			BinaryWriter dos_8 = new BinaryWriter(bos_7);
			RpcBinarySerializer.writeString(hello,dos_8);
			m_6.paramstream = bos_7.ToArray();
			m_6.prx = this;
			m_6.async = async;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_5 = this.conn.sendMessage(m_6);
		if(!r_5){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
	
	public void bidirection(){
bidirection(RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void bidirection(int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 2;
		m_2.opidx = 3;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_3 = false;
		try{
			if( timeout > 0) _rc_3 = m_2.ev.WaitOne(timeout);
			else _rc_3 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_3 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
	}	
	
	public void bidirection_oneway(Dictionary<string,string> props){
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 2;
		m_2.opidx = 3;
		m_2.paramsize = 0;
		m_2.extra.setProperties(props);
		try{
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void bidirection_async(Server_AsyncCallBack async,Dictionary<string,string> props){
		bidirection_async(async,props,null);
	}	
	
	public void bidirection_async(Server_AsyncCallBack async){
		bidirection_async(async,null,null);
	}	
	
	public void bidirection_async(Server_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_3 = false;
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
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_3 = this.conn.sendMessage(m_4);
		if(!r_3){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}


public class Server_AsyncCallBack: RpcAsyncCallBackBase{
	// following functions should be overrided in user code.
	public void echo(string result,RpcProxyBase proxy,object cookie){
	}	
	
	public void timeout(RpcProxyBase proxy,object cookie){
	}	
	
	public void heartbeat(RpcProxyBase proxy,object cookie){
	}	
	
	public void bidirection(RpcProxyBase proxy,object cookie){
	}	
	
	public override void callReturn(RpcMessage m1,RpcMessage m2){
		bool r = false;
		MemoryStream d = new MemoryStream(m2.paramstream);
		BinaryReader reader = new BinaryReader(d);
		if( m1.opidx == 0 ){
			string b_5 = "";
			b_5 = RpcBinarySerializer.readString(reader);
			echo(b_5,m1.prx,m1.cookie);
		}		
		if( m1.opidx == 1 ){
			timeout(m1.prx,m1.cookie);
		}		
		if( m1.opidx == 2 ){
			heartbeat(m1.prx,m1.cookie);
		}		
		if( m1.opidx == 3 ){
			bidirection(m1.prx,m1.cookie);
		}		
	}	
}

public class Server : RpcServant{
	//# -- INTERFACE -- 
	public Server(){
		this.delegate_ = new Server_delegate(this);
	}	
	
	
	public virtual string echo(string text,RpcContext ctx){
		return "";
	}	
	
	public virtual void timeout(int secs,RpcContext ctx){
	}	
	
	public virtual void heartbeat(string hello,RpcContext ctx){
	}	
	
	public virtual void bidirection(RpcContext ctx){
	}	
}

public class Server_delegate : RpcServantDelegate {
	
	Server inst = null;
	public Server_delegate(Server inst){
		this.ifidx = 2;
		this.inst = inst;
	}	
	
	public override bool invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		if(m.opidx == 1 ){
			return func_1_delegate(m);
		}		
		if(m.opidx == 2 ){
			return func_2_delegate(m);
		}		
		if(m.opidx == 3 ){
			return func_3_delegate(m);
		}		
		return false;
	}	
	
	// func: echo
	bool func_0_delegate(RpcMessage m){
		bool r = false;
		MemoryStream bos = new MemoryStream(m.paramstream);
		BinaryReader reader = new BinaryReader(bos);
		string text;
		text = RpcBinarySerializer.readString(reader);
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		string cr;
		cr = servant.echo(text,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		mr.conn = m.conn;
		mr.ifidx = m.ifidx;
		mr.call_id = m.call_id;
		if(m.extra.getProperties().ContainsKey("__user_id__")){
			mr.extra.setPropertyValue("__user_id__",m.extra.getPropertyValue("__user_id__"));
		}		
		try{
			MemoryStream _bos_9 = new MemoryStream();
			BinaryWriter dos = new BinaryWriter(_bos_9);
			RpcBinarySerializer.writeString(cr,dos);
			mr.paramsize = 1;
			mr.paramstream = _bos_9.ToArray();
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	
	
	// func: timeout
	bool func_1_delegate(RpcMessage m){
		bool r = false;
		MemoryStream bos = new MemoryStream(m.paramstream);
		BinaryReader reader = new BinaryReader(bos);
		int secs;
		secs = RpcBinarySerializer.readInt(reader);
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.timeout(secs,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	// func: heartbeat
	bool func_2_delegate(RpcMessage m){
		bool r = false;
		MemoryStream bos = new MemoryStream(m.paramstream);
		BinaryReader reader = new BinaryReader(bos);
		string hello;
		hello = RpcBinarySerializer.readString(reader);
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.heartbeat(hello,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	// func: bidirection
	bool func_3_delegate(RpcMessage m){
		bool r = false;
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.bidirection(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}


public class ITerminalProxy:RpcProxyBase{
	//-- interface proxy -- 
	
	public ITerminalProxy(RpcConnection conn){
		this.conn = conn;
	}	
	
	public static ITerminalProxy create(string host,int port,bool ssl_enable){
		int type = RpcConstValue.CONNECTION_SOCK;
		if (ssl_enable) type |= RpcConstValue.CONNECTION_SSL;
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
			RpcCommunicator.instance().getLogger().error(e.ToString());
		}		
	}	
	
	public void onMessage(string message){
onMessage(message,RpcCommunicator.instance().getProperty_DefaultCallWaitTime(),null);		
	}	
	// timeout - msec ,  0 means waiting infinitely
	public void onMessage(string message,int timeout,Dictionary<string,string> props) {
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL);
		m_2.ifidx = 3;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeString(message,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
		bool _rc_5 = false;
		try{
			if( timeout > 0) _rc_5 = m_2.ev.WaitOne(timeout);
			else _rc_5 = m_2.ev.WaitOne( RpcCommunicator.instance().getProperty_DefaultCallWaitTime() );
		}catch(Exception e){
			RpcCommunicator.instance().logger.error(e.ToString());
			throw new RpcException(RpcException.RPCERROR_INTERNAL_EXCEPTION,e.ToString());
		}		
		if( _rc_5 == false){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT);
		}		
		if (m_2.errcode != RpcException.RPCERROR_SUCC){
			throw new RpcException(m_2.errcode);
		}		
		if( m_2.result == null){
			throw new RpcException(RpcException.RPCERROR_TIMEOUT,"response is null");
		}		
	}	
	
	public void onMessage_oneway(string message,Dictionary<string,string> props){
		bool r_1 = false;
		RpcMessage m_2 = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m_2.ifidx = 3;
		m_2.opidx = 0;
		m_2.paramsize = 1;
		m_2.extra.setProperties(props);
		try{
			MemoryStream bos_3 = new MemoryStream();
			BinaryWriter dos_4 = new BinaryWriter(bos_3);
			RpcBinarySerializer.writeString(message,dos_4);
			m_2.paramstream = bos_3.ToArray();
			m_2.prx = this;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_1 = this.conn.sendMessage(m_2);
		if(!r_1){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	public void onMessage_async(string message,ITerminal_AsyncCallBack async,Dictionary<string,string> props){
		onMessage_async(message,async,props,null);
	}	
	
	public void onMessage_async(string message,ITerminal_AsyncCallBack async){
		onMessage_async(message,async,null,null);
	}	
	
	public void onMessage_async(string message,ITerminal_AsyncCallBack async,Dictionary<string,string> props,object cookie){
		bool r_5 = false;
		RpcMessage m_6 = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m_6.ifidx = 3;
		m_6.opidx = 0;
		m_6.paramsize = 1;
		m_6.extra.setProperties(props);
		m_6.cookie = cookie;
		try{
			MemoryStream bos_7 = new MemoryStream();
			BinaryWriter dos_8 = new BinaryWriter(bos_7);
			RpcBinarySerializer.writeString(message,dos_8);
			m_6.paramstream = bos_7.ToArray();
			m_6.prx = this;
			m_6.async = async;
		}catch(Exception e){
			throw new RpcException(RpcException.RPCERROR_DATADIRTY,e.ToString());
		}		
		r_5 = this.conn.sendMessage(m_6);
		if(!r_5){
			throw new RpcException(RpcException.RPCERROR_SENDFAILED);
		}		
	}	
	
	
}


public class ITerminal_AsyncCallBack: RpcAsyncCallBackBase{
	// following functions should be overrided in user code.
	public void onMessage(RpcProxyBase proxy,object cookie){
	}	
	
	public override void callReturn(RpcMessage m1,RpcMessage m2){
		bool r = false;
		MemoryStream d = new MemoryStream(m2.paramstream);
		BinaryReader reader = new BinaryReader(d);
		if( m1.opidx == 0 ){
			onMessage(m1.prx,m1.cookie);
		}		
	}	
}

public class ITerminal : RpcServant{
	//# -- INTERFACE -- 
	public ITerminal(){
		this.delegate_ = new ITerminal_delegate(this);
	}	
	
	
	public virtual void onMessage(string message,RpcContext ctx){
	}	
}

public class ITerminal_delegate : RpcServantDelegate {
	
	ITerminal inst = null;
	public ITerminal_delegate(ITerminal inst){
		this.ifidx = 3;
		this.inst = inst;
	}	
	
	public override bool invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: onMessage
	bool func_0_delegate(RpcMessage m){
		bool r = false;
		MemoryStream bos = new MemoryStream(m.paramstream);
		BinaryReader reader = new BinaryReader(bos);
		string message;
		message = RpcBinarySerializer.readString(reader);
		ITerminal servant = (ITerminal)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.onMessage(message,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}

}
