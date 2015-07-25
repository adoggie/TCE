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

public class ITerminalGatewayServer_AsyncCallBack extends RpcAsyncCallBackBase{
	// following functions should be ovrrided in user code.
	public void ping(RpcProxyBase proxy,Object cookie){
	}	
	
	@Override
	public void callReturn(RpcMessage m1,RpcMessage m2){
		boolean r = false;
		ByteBuffer d = ByteBuffer.wrap(m2.paramstream);
		if(m1.opidx == 0){
			ping(m1.prx,m1.cookie);
		}		
	}	
}
