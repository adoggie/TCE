package tce;
	
import tce.RpcMessage;

public class RpcMessageReturn extends RpcMessage{
	
	public  RpcMessageReturn(){
		super(RpcMessage.RETURN);
	}

	public RpcMessageReturn(int seq,int errcode){
		this();
		this.sequence = seq;
		this.errcode = errcode;
	}

	public void send(RpcConnection conn) {
		conn.sendMessage(this);
	}
}