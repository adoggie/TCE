package easymq;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	

import easymq.*;
import tce.*;
import java.nio.*;
import java.util.*;

public class IClient_AsyncCallBack extends RpcAsyncCallBackBase{
	// following functions should be ovrrided in user code.
	public void onRecvData(RpcProxyBase proxy){
	}	
	
	public void test(byte[] result,RpcProxyBase proxy){
	}	
	
	@Override
	public void callReturn(RpcMessage m1,RpcMessage m2){
		boolean r = false;
		ByteBuffer d = ByteBuffer.wrap(m2.paramstream);
		if(m1.opidx == 1){
			byte[] b_13 = new byte[0];
			int _s_14 = d.getInt();
			b_13 = new byte[_s_14];
			d.get(b_13);
			test(b_13,m1.prx);
		}		
	}	
}
