
package tce;

//import java.util.*;

public class RpcServantDelegate{
	public String index; // for xml 
	public int 	ifidx;
	public RpcAdapter adapter = null;
	//public Hashtable<String,>
	public RpcServantDelegate(){
		
	}
	
	public RpcMessage invoke(RpcMessage m) throws Exception{
		// if function have return value, it must be RpcMessageReturn.
		return null;
	}
	
}