package test;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	
import tce.*;
import test.BaseServer_delegate;
import test.*;
import java.util.*;

public class BaseServer extends RpcServant{
	//# -- INTERFACE -- 
	public BaseServer(){
		super();
		this.delegate = new BaseServer_delegate(this);
	}	
	
	
	public String datetime(RpcContext ctx){
		return "";
	}	
}
