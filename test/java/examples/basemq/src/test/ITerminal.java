package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import test.ITerminal_delegate;
import test.*;
import java.util.*;

public class ITerminal extends RpcServant{
	//# -- INTERFACE -- 
	public ITerminal(){
		super();
		this.delegate = new ITerminal_delegate(this);
	}	
	
	
	public void onMessage(String message,RpcContext ctx){
	}	
}
