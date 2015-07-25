package easymq;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	

import easymq.*;
import java.io.*;
import java.nio.*;
import java.util.*;

public class mq_handle_t{
// -- STRUCT -- 
	public  String token = "";
	
	//构造函数
	public mq_handle_t(){
		
	}	
	
	// return xml string
	public boolean marshall(DataOutputStream d){
		try{
			byte[] sb_1 = token.getBytes();
			d.writeInt(sb_1.length);
			d.write(sb_1,0,sb_1.length);
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
	public boolean unmarshall(ByteBuffer d){
		boolean r = false;
		try{
			int _sb_1 = d.getInt();
			byte[] _sb_2 = new byte[_sb_1];
			d.get(_sb_2);
			this.token = new String(_sb_2);
		}catch(Exception e){
			tce.RpcCommunicator.instance().getLogger().error(e.getMessage());
			r = false;
			return r;
		}		
		return true;
	}	
	 // --  end function -- 
	
}
