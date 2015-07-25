package easymq;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import easymq.IClient_delegate;
import easymq.*;
import java.util.*;

public class IClient extends RpcServant{
	//# -- INTERFACE -- 
	public IClient(){
		super();
		this.delegate = new IClient_delegate(this);
	}	
	
	
	public void onRecvData(mq_handle_t mq,message_t msg,RpcContext ctx){
	}	
	
	public byte[] test(byte[] data,byte[] data2,RpcContext ctx){
		return new byte[0];
	}	
}
