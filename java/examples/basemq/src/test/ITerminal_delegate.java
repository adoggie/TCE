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
import test.ITerminal;

public class ITerminal_delegate extends RpcServantDelegate {
	
	ITerminal inst = null;
	public ITerminal_delegate(ITerminal inst){
		this.ifidx = 3;
		this.inst = inst;
	}	
	
	@Override
	public boolean invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: onMessage
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ByteBuffer d = ByteBuffer.wrap(m.paramstream);
		String message;
		int v_12 = d.getInt();
		byte[] _sb_13 = new byte[v_12];
		d.get(_sb_13);
		message = new String(_sb_13);
		ITerminal servant = (ITerminal)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.onMessage(message,ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}
