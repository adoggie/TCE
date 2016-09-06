package tce;

/**
 * Created by scott on 7/12/15.
 */
public class RpcEndPoint {
	public final static String EP_QPID ="qpid";
	public final static String EP_SOCKET ="socket";
	public final static int AF_READ = 1;
	public final static int AF_WRITE = 2;



	public String name;
	public String host;
	public int  port;
	public String address;
	public String type;
	public boolean ssl = false;

	public RpcEndPoint(String name,String  host,int port,String address,String type) {
		this.name = name;
		this.host = host;
		this.port = port ;
		this.address = address;
		this.type = type;
	}

	public RpcEndPoint(String name,String  host,int port,String address) {
		this.name = name;
		this.host = host;
		this.port = port ;
		this.address = address;
		this.type = EP_QPID;
	}

	public RpcEndPoint(String host,int port){
		this.host = host;
		this.port = port;
	}
}
