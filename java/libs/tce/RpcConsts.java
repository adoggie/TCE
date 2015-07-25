
package tce;

public class RpcConsts{

	public static final int RPCERROR_SUCC = 0;
	public static final int RPCERROR_SENDFAILED =1;
	public static final int RPCERROR_DATADIRTY= 3;
	public static final int RPCERROR_TIMEOUT = 2;
	public static final int RPCERROR_INTERFACE_NOTFOUND = 4;
	public static final int RPCERROR_UNSERIALIZE_FAILED = 5;
	public static final int RPCERROR_REMOTEMETHOD_EXCEPTION = 6;
	public static final int RPCERROR_DATA_INSUFFICIENT = 7;
	public static final int RPCERROR_REMOTE_EXCEPTION = 8;
	public static final int RPCERROR_CONNECT_UNREACHABLE = 101;
	public static final int RPCERROR_CONNECT_FAILED  = 102;
	public static final int RPCERROR_CONNECT_REJECT = 103;
	public static final int RPCERROR_CONNECTION_LOST = 104;
	public static final int RPCERROR_INTERNAL_EXCEPTION = 105;
	
	public static String ErrorString(int err){
		String str="";
		if(err == RPCERROR_SUCC) str = "RPCERROR_SUCC";
		else if(err == RPCERROR_SENDFAILED) str="RPCERROR_SENDFAILED";
		else if(err == RPCERROR_DATADIRTY) str="RPCERROR_DATADIRTY";
		else if(err == RPCERROR_TIMEOUT) str="RPCERROR_TIMEOUT";
		else if(err == RPCERROR_INTERFACE_NOTFOUND) str="RPCERROR_INTERFACE_NOTFOUND";
		else if(err == RPCERROR_UNSERIALIZE_FAILED) str="RPCERROR_UNSERIALIZE_FAILED";
		else if(err == RPCERROR_REMOTEMETHOD_EXCEPTION) str="RPCERROR_REMOTEMETHOD_EXCEPTION";
		else if(err == RPCERROR_DATA_INSUFFICIENT) str="RPCERROR_DATA_INSUFFICIENT";
		else if(err == RPCERROR_REMOTE_EXCEPTION) str="RPCERROR_REMOTE_EXCEPTION";
		else if(err == RPCERROR_CONNECT_UNREACHABLE) str="RPCERROR_CONNECT_UNREACHABLE";
		else if(err == RPCERROR_CONNECT_FAILED) str="RPCERROR_CONNECT_FAILED";
		else if(err == RPCERROR_CONNECT_REJECT) str="RPCERROR_CONNECT_REJECT";
		else if(err == RPCERROR_CONNECTION_LOST) str="RPCERROR_CONNECTION_LOST";
		else if(err == RPCERROR_INTERNAL_EXCEPTION) str="RPCERROR_INTERNAL_EXCEPTION";
		
		return str;
		
	}
	
	
	//
	public static final int COMPRESS_NONE = 0;
	public static final int COMPRESS_ZLIB = 1;
	public static final int COMPRESS_BZIP2 = 2;
	
	public static final int ENCRYPT_NONE = 0;
	public static final int ENCRYPT_MD5  = 1;
	public static final int ENCRYPT_DES  = 2;
	
	public static final int MSGTYPE_RPC = 1;
	public static final int MSGTYPE_NORPC = 2;
	
	public static final int CONNECTION_UNKNOWN = 0;
	public static final int CONNECTION_SOCK = 1;
	public static final int CONNECTION_HTTP = 2;
	public static final int CONNECTION_SSL = 0x10; // added by scott 2014.6.21
	
	public static final int MSG_ENCODE_BIN = 0x10;
	public static final int MSG_ENCODE_XML = 0x20;
	
	
	public static final int ASYNC_RPCMSG = 0x01;

	public static String EXTRA_DATA_MQ_RETURN = "__mq_return__";
	public static String EXTRA_DATA_USER_ID = "__user_id__";
}


