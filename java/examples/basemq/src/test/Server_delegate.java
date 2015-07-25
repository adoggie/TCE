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
import test.Server;

public class Server_delegate extends RpcServantDelegate {
	
	Server inst = null;
	public Server_delegate(Server inst){
		this.ifidx = 2;
		this.inst = inst;
	}	
	
	@Override
	public boolean invoke(RpcMessage m){
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
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		String text;
		int v_11 = d.getInt();
		byte[] _sb_12 = new byte[v_11];
		d.get(_sb_12);
		text = new String(_sb_12);
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		String cr;
		cr = servant.echo(text,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		mr.conn = m.conn;
		mr.ifidx = m.ifidx;
		mr.call_id = m.call_id;
		if(m.extra.getProperties().containsKey("__user_id__")){
			mr.extra.setPropertyValue("__user_id__",m.extra.getPropertyValue("__user_id__"));
		}		
		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			byte[] sb_13 = cr.getBytes();
			dos.writeInt(sb_13.length);
			dos.write(sb_13,0,sb_13.length);
			mr.paramsize = 1;
			mr.paramstream = bos.toByteArray();
		}catch(Exception e){
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	
	
	// func: timeout
	boolean func_1_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		Integer secs;
		secs = d.getInt();
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.timeout(secs,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	// func: heartbeat
	boolean func_2_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		String hello;
		int v_14 = d.getInt();
		byte[] _sb_15 = new byte[v_14];
		d.get(_sb_15);
		hello = new String(_sb_15);
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.heartbeat(hello,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	// func: bidirection
	boolean func_3_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		Server servant = (Server)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.bidirection(ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}
