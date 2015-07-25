package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import test.Server_delegate;
import test.*;
import java.util.*;

public class Server extends RpcServant{
	//# -- INTERFACE -- 
	public Server(){
		super();
		this.delegate = new Server_delegate(this);
	}	
	
	
	public String echo(String text,RpcContext ctx){
		return "";
	}	
	
	public void timeout(Integer secs,RpcContext ctx){
	}	
	
	public void heartbeat(String hello,RpcContext ctx){
	}	
	
	public void bidirection(RpcContext ctx){
	}	
}
