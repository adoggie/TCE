
package tce;

import tce.RpcConnection;

public class RpcProxyBase{
	public RpcConnection conn = null;
	public Object delta = null;

	public RpcProxyBase(){

	}

	public void setToken(String token){
		if(conn!=null){
			conn.close();
			conn.setToken(token);
		}
	}
}
