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

public class BaseServer_AsyncCallBack extends RpcAsyncCallBackBase{
	// following functions should be ovrrided in user code.
	public void datetime(String result,RpcProxyBase proxy,Object cookie){
	}	
	
	@Override
	public void callReturn(RpcMessage m1,RpcMessage m2){
		boolean r = false;
		ByteBuffer d = ByteBuffer.wrap(m2.paramstream);
		if(m1.opidx == 0){
			String b_10 = "";
			int v_11 = d.getInt();
			byte[] _sb_12 = new byte[v_11];
			d.get(_sb_12);
			b_10 = new String(_sb_12);
			datetime(b_10,m1.prx,m1.cookie);
		}		
	}	
}
