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

public class IServer_AsyncCallBack extends RpcAsyncCallBackBase{
	// following functions should be ovrrided in user code.
	public void register(String result,RpcProxyBase proxy){
	}	
	
	public void heartbeat(RpcProxyBase proxy){
	}	
	
	public void openMQ(mq_handle_t result,RpcProxyBase proxy){
	}	
	
	public void closeMQ(RpcProxyBase proxy){
	}	
	
	public void writeMQ(RpcProxyBase proxy){
	}	
	
	public void getMqStaticstic(Vector<mq_info_t> result,RpcProxyBase proxy){
	}	
	
	@Override
	public void callReturn(RpcMessage m1,RpcMessage m2){
		boolean r = false;
		ByteBuffer d = ByteBuffer.wrap(m2.paramstream);
		if(m1.opidx == 0){
			String b_9 = "";
			int _sb_10 = d.getInt();
			byte[] _sb_11 = new byte[_sb_10];
			d.get(_sb_11);
			b_9 = new String(_sb_11);
			register(b_9,m1.prx);
		}		
		if(m1.opidx == 2){
			mq_handle_t b_12 = new mq_handle_t();
			r = b_12.unmarshall(d);
			openMQ(b_12,m1.prx);
		}		
		if(m1.opidx == 5){
			Vector<mq_info_t> b_13 = new Vector<mq_info_t>();
			mq_info_list_thlp c_14 = new mq_info_list_thlp(b_13);
			r = c_14.unmarshall(d);
			getMqStaticstic(b_13,m1.prx);
		}		
	}	
}
