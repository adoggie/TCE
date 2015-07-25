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
import test.ITerminalGatewayServer;

public class ITerminalGatewayServer_delegate extends RpcServantDelegate {
	
	ITerminalGatewayServer inst = null;
	public ITerminalGatewayServer_delegate(ITerminalGatewayServer inst){
		this.ifidx = 1;
		this.inst = inst;
	}	
	
	@Override
	public boolean invoke(RpcMessage m){
		if(m.opidx == 0 ){
			return func_0_delegate(m);
		}		
		return false;
	}	
	
	// func: ping
	boolean func_0_delegate(RpcMessage m){
		boolean r= false;
		r = false;
		ITerminalGatewayServer servant = (ITerminalGatewayServer)this.inst;
		RpcContext ctx = new RpcContext();
		ctx.msg = m;
		servant.ping(ctx);
		if( (m.calltype & tce.RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	
	
}
