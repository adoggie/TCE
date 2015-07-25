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

public class message_t{
// -- STRUCT -- 
	public  byte[] data = new byte[0];
	public  HashMap< String,String > props_ = new HashMap<String,String>();
	
	//构造函数
	public message_t(){
		
	}	
	
	// return xml string
	public boolean marshall(DataOutputStream d){
		try{
			d.writeInt(data.length);
			d.write(this.data,0,data.length);
			properties_thlp _b_1 = new properties_thlp(this.props_);
			_b_1.marshall(d);
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
	public boolean unmarshall(ByteBuffer d){
		boolean r = false;
		try{
			int _s_1 = d.getInt();
			this.data = new byte[_s_1];
			d.get(this.data);
			properties_thlp _b_2 = new properties_thlp(this.props_);
			r = _b_2.unmarshall(d);
			if(!r){return false;}
		}catch(Exception e){
			tce.RpcCommunicator.instance().getLogger().error(e.getMessage());
			r = false;
			return r;
		}		
		return true;
	}	
	 // --  end function -- 
	
}
