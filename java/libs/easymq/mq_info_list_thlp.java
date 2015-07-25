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

public class mq_info_list_thlp{
	//# -- SEQUENCE --
	
	public Vector<mq_info_t> ds = null;
	public mq_info_list_thlp(Vector<mq_info_t> ds){
		this.ds = ds;
	}	
	
	public boolean marshall(DataOutputStream d){
		try{
			d.writeInt(this.ds.size());
			for(mq_info_t item : this.ds){
				item.marshall(d);
			}			
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
	public boolean unmarshall(ByteBuffer d){
		int _size_3 = 0;
		try{
			_size_3 = d.getInt();
			for(int _p=0;_p < _size_3;_p++){
				mq_info_t _b_4 = new mq_info_t();
				_b_4.unmarshall(d);
				this.ds.add(_b_4);
			}			
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
}

