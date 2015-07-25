package tce;

//import tce.RpcConnection;
import tce.RpcMessage;

public class RpcAsyncCallBackBase {
	public Object delta = null;
	private String _token = null;
	private boolean _execInMainThread = false;

	public void callReturn(RpcMessage m1,RpcMessage m2){

	}

	public void onError(int errorcode){

	}


}
