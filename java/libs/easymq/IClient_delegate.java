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
import easymq.IClient;

public class IClient_delegate extends RpcServantDelegate {
	
	IClient inst = null;
	public IClient_delegate(IClient inst){
		this.ifidx = 0;
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
		return false;
	}	
	
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		mq_handle_t mq = new mq_handle_t();
		mq.unmarshall(d);
		message_t msg = new message_t();
		msg.unmarshall(d);
		IClient servant = (IClient)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.onRecvData(mq,msg,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	boolean func_1_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		int _s_15 = d.getInt();
		byte[] data = new byte[_s_15];
		d.get(data);
		int _s_16 = d.getInt();
		byte[] data2 = new byte[_s_16];
		d.get(data2);
		IClient servant = (IClient)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		byte[] cr;
		cr = servant.test(data,data2,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			dos.writeInt(data2.length);
			dos.write(data2,0,data2.length);
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
