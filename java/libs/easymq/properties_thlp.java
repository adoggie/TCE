package easymq;
//import tce.*;
//import javax.xml.parsers.*;
//import org.w3c.dom.*;
//import java.io.*;
//import java.nio.*;
//import java.util.*;
	

import easymq.*;
import tce.*;
import java.util.*;
import java.io.*;
import java.nio.*;

public class properties_thlp {
	//# -- THIS IS DICTIONARY! --
	public HashMap< String,String > ds = null;
	
	public properties_thlp(HashMap< String,String > ds){
		this.ds = ds;
	}	
	
	public boolean marshall(DataOutputStream d){
		try{
			d.writeInt(this.ds.size());
			for( String _k_1 : this.ds.keySet()){
				String _v_2 = ds.get(_k_1);
				byte[] sb_3 = _k_1.getBytes();
				d.writeInt(sb_3.length);
				d.write(sb_3,0,sb_3.length);
				byte[] sb_4 = _v_2.getBytes();
				d.writeInt(sb_4.length);
				d.write(sb_4,0,sb_4.length);
			}			
		}catch(Exception e){
			return false;
		}		
		return true;
	}	
	
	// unmarshall()
	public boolean unmarshall(ByteBuffer d){
		int _size_1 = 0;
		try{
			_size_1 = d.getInt();
			for(int _p=0;_p < _size_1;_p++){
				String _k_2 = "";
				int _sb_5 = d.getInt();
				byte[] _sb_6 = new byte[_sb_5];
				d.get(_sb_6);
				_k_2 = new String(_sb_6);
				String _v_3 = "";
				int _sb_8 = d.getInt();
				byte[] _sb_9 = new byte[_sb_8];
				d.get(_sb_9);
				_v_3 = new String(_sb_9);
				this.ds.put(_k_2,_v_3);
			}			
		}catch(Exception e){
			return false;
		}		
		
		return true;
	}	
}
//-- end Dictonary Class definations --

