
package tce;

import tce.RpcCommAdapter;
import tce.RpcMessage;
//import java.util.*;

public class RpcServantDelegate{
	public String index; // for xml 
	public int 	ifidx;
	public RpcCommAdapter adapter = null;
	//public Hashtable<String,>
	public RpcServantDelegate(){
		
	}
	
	public boolean invoke(RpcMessage m){
		
		return true;
	}
	
}