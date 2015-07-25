package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import test.ITerminalGatewayServer_delegate;
import test.*;
import java.util.*;

public class ITerminalGatewayServer extends RpcServant{
	//# -- INTERFACE -- 
	public ITerminalGatewayServer(){
		super();
		this.delegate = new ITerminalGatewayServer_delegate(this);
	}	
	
	
	public void ping(RpcContext ctx){
	}	
}
