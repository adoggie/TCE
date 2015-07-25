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
import easymq.IServer;

public class IServer_delegate extends RpcServantDelegate {
	
	IServer inst = null;
	public IServer_delegate(IServer inst){
		this.ifidx = 1;
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
		if(m.opidx == 4 ){
			return func_4_delegate(m);
		}		
		if(m.opidx == 5 ){
			return func_5_delegate(m);
		}		
		return false;
	}	
	
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		String user;
		int _sb_15 = d.getInt();
		byte[] _sb_16 = new byte[_sb_15];
		d.get(_sb_16);
		user = new String(_sb_16);
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		String cr;
		cr = servant.register(user,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			byte[] sb_17 = cr.getBytes();
			dos.writeInt(sb_17.length);
			dos.write(sb_17,0,sb_17.length);
			mr.paramsize = 1;
			mr.paramstream = bos.toByteArray();
		}catch(Exception e){
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	
	
	boolean func_1_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.heartbeat(ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	boolean func_2_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		String name;
		int _sb_18 = d.getInt();
		byte[] _sb_19 = new byte[_sb_18];
		d.get(_sb_19);
		name = new String(_sb_19);
		Integer type;
		type = d.getInt();
		Integer flags;
		flags = d.getInt();
		Integer mode;
		mode = d.getInt();
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		mq_handle_t cr;
		cr = servant.openMQ(name,type,flags,mode,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			cr.marshall(dos);
			mr.paramsize = 1;
			mr.paramstream = bos.toByteArray();
		}catch(Exception e){
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	
	
	boolean func_3_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		mq_handle_t mq = new mq_handle_t();
		mq.unmarshall(d);
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.closeMQ(mq,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	boolean func_4_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		mq_handle_t mq = new mq_handle_t();
		mq.unmarshall(d);
		message_t msg = new message_t();
		msg.unmarshall(d);
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.writeMQ(mq,msg,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
	boolean func_5_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		IServer servant = (IServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		Vector<mq_info_t> cr;
		cr = servant.getMqStaticstic(ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		RpcMessage mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			mq_info_list_thlp _c_20 = new mq_info_list_thlp(cr);
			_c_20.marshall(dos);
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
