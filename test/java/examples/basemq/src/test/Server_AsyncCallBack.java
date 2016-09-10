package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	

import test.*;
import tce.*;
import java.nio.*;
import java.util.*;

public class Server_AsyncCallBack extends RpcAsyncCallBackBase{
	// following functions should be ovrrided in user code.
	public void echo(String result,RpcProxyBase proxy,Object cookie){
	}	
	
	public void timeout(RpcProxyBase proxy,Object cookie){
	}	
	
	public void heartbeat(RpcProxyBase proxy,Object cookie){
	}	
	
	public void bidirection(RpcProxyBase proxy,Object cookie){
	}	
	
	@Override
	public void callReturn(RpcMessage m1,RpcMessage m2){
		boolean r = false;
		ByteBuffer d = ByteBuffer.wrap(m2.paramstream);
		if(m1.opidx == 0){
			String b_5 = "";
			int v_6 = d.getInt();
			byte[] _sb_7 = new byte[v_6];
			d.get(_sb_7);
			b_5 = new String(_sb_7);
			echo(b_5,m1.prx,m1.cookie);
		}		
		if(m1.opidx == 1){
			timeout(m1.prx,m1.cookie);
		}		
		if(m1.opidx == 2){
			heartbeat(m1.prx,m1.cookie);
		}		
		if(m1.opidx == 3){
			bidirection(m1.prx,m1.cookie);
		}		
	}	
}
