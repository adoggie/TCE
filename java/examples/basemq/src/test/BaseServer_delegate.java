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
import test.BaseServer;

public class BaseServer_delegate extends RpcServantDelegate {
	
	BaseServer inst = null;
	public BaseServer_delegate(BaseServer inst){
		this.ifidx = 0;
		this.inst = inst;
	}	
	
	@Override
	public boolean invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: datetime
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		BaseServer servant = (BaseServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		String cr;
		cr = servant.datetime(ctx);
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
	
}
