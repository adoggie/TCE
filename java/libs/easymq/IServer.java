package easymq;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import easymq.IServer_delegate;
import easymq.*;
import java.util.*;

public class IServer extends RpcServant{
	//# -- INTERFACE -- 
	public IServer(){
		super();
		this.delegate = new IServer_delegate(this);
	}	
	
	
	public String register(String user,RpcContext ctx){
		return "";
	}	
	
	public void heartbeat(RpcContext ctx){
	}	
	
	public mq_handle_t openMQ(String name,Integer type,Integer flags,Integer mode,RpcContext ctx){
		return new mq_handle_t();
	}	
	
	public void closeMQ(mq_handle_t mq,RpcContext ctx){
	}	
	
	public void writeMQ(mq_handle_t mq,message_t msg,RpcContext ctx){
	}	
	
	public Vector<mq_info_t> getMqStaticstic(RpcContext ctx){
		return new Vector<mq_info_t>();
	}	
}
