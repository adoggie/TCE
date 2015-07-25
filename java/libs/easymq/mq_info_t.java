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

public class mq_info_t{
// -- STRUCT -- 
	public  String name = "";
	public  Integer type = Integer.valueOf(0);
	public  Long inpkgs = Long.valueOf(0);
	public  Long outpkgs = Long.valueOf(0);
	public  Long inbytes = Long.valueOf(0);
	public  Long outbytes = Long.valueOf(0);
	
	//构造函数
	public mq_info_t(){
		
	}	
	
	// return xml string
	public boolean marshall(DataOutputStream d){
		try{
			byte[] sb_1 = name.getBytes();
			d.writeInt(sb_1.length);
			d.write(sb_1,0,sb_1.length);
			d.writeInt(type);
			d.writeLong(inpkgs);
			d.writeLong(outpkgs);
			d.writeLong(inbytes);
			d.writeLong(outbytes);
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
			this.name = new String(_sb_2);
			this.type = d.getInt();
			this.inpkgs = d.getLong();
			this.outpkgs = d.getLong();
			this.inbytes = d.getLong();
			this.outbytes = d.getLong();
		}catch(Exception e){
			tce.RpcCommunicator.instance().getLogger().error(e.getMessage());
			r = false;
			return r;
		}		
		return true;
	}	
	 // --  end function -- 
	
}
