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

public class datastream_thlp{
	//# -- SEQUENCE --
	
	public Vector<Byte> ds = null;
	public datastream_thlp(Vector<Byte> ds){
		this.ds = ds;
	}	
	
	public boolean marshall(DataOutputStream d){
		try{
			d.writeInt(this.ds.size());
			for(Byte item : this.ds){
				d.writeByte(item);
			}			
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
	public boolean unmarshall(ByteBuffer d){
		int _size_1 = 0;
		try{
			_size_1 = d.getInt();
			for(int _p=0;_p < _size_1;_p++){
				Byte _o = 0;
				_o = d.get();
				this.ds.add(_o);
			}			
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
}

