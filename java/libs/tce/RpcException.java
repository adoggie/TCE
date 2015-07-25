
package tce;

import java.lang.Exception;
	
public class RpcException extends Exception{
	private static final long serialVersionUID = 1;
	int 	_errcode = 0;
	String _msg="";
	
	
	public RpcException(int errcode){
		super();
		_errcode = errcode;
	}
	
	public RpcException(int errcode,String msg){
		super();
		_errcode = errcode;
		_msg = msg;
	}
	
	@Override
	public String getMessage(){
		return what();
	}
	
	public String what() {
		//throw new RpcException(0,"");
		return RpcConsts.ErrorString(_errcode)+ " " + _msg;
	}

	@Override
	public String toString(){
		return what();
	}
}

	

