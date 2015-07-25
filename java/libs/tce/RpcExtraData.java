package tce;

import java.util.*;
import java.io.*;
import java.nio.*;


public class RpcExtraData {
//	public final static int NODATA 			= 0;
//	public final static int BYTESTREAM 	= 1;
//	public final static int STRING				= 2;
//	public final static int STRING_DICT	= 3;
//	public final static int STRING_LIST 	= 4;

	RpcExtraData(){

	}

	public boolean marshall(DataOutputStream d ){
		try{
			if(_props ==null){
				_props = new HashMap<String,String >();
			}
			d.writeInt(_props.size());
			String key,val;
			Iterator<String> iterator = _props.keySet().iterator();
			while( iterator.hasNext()){
				key = iterator.next();
				val = _props.get(key);
				if(val == null){
					val = "";
				}
				d.writeInt(key.length());
				d.write(key.getBytes(),0,key.length());
				d.writeInt(val.length());
				d.write(val.getBytes(),0,val.length());
			}
		}catch(Exception e){
			return false;
		}
		return true;
	}

	public boolean unmarshall(ByteBuffer d){
		try{
			int size = d.getInt();
			String key,val;
			byte[] bytes ;
			int len;
			for(int n=0;n<size;n++){
				len = d.getInt();
				bytes = new byte[len];
				d.get(bytes);
				key = new String(bytes);
				len = d.getInt();
				bytes = new byte[len];
				d.get(bytes);
				val = new String(bytes);
				_props.put(key,val);
			}
		}catch(Exception e ){
			RpcCommunicator.instance().getLogger().error(e.toString());
			return false;
		}
		return true;
	}

	public HashMap<String,String > getProperties(){
		return _props;
	}

	public String getPropertyValue(String key){
		HashMap<String,String > props = getProperties();
		if(props.containsKey(key)){
			return props.get(key);
		}
		return null;
	}

	public void setPropertyValue(String key,String value){
		if(_props == null){
			_props = new HashMap<String,String >();
		}
		_props.put(key, value);
	}

	public RpcExtraData setProperties(HashMap<String,String> props){
		if(props!=null){
			_props = props;
		}
		return this;
	}

	public int size(){
		return datasize() + 4 ;
	}

	public int datasize(){
		int size = 0;

		String key,val;
		Iterator<String> iterator = _props.keySet().iterator();
		while( iterator.hasNext()){
			key = iterator.next();
			val = _props.get(key);
			size+=key.length() + val.length() + 8;
		}
		return size;
	}




//	private int 	_type = NODATA;
//	private byte[]  _data = null;
//
	HashMap<String,String > _props = new HashMap<String,String >();

}
