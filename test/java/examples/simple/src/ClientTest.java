import tce.RpcCommunicator;
import tce.RpcContext;
import tce.RpcProxyBase;
import test.ITerminal;
import test.ITerminalGatewayServerProxy;
import test.ServerProxy;
import test.Server_AsyncCallBack;

/**
 * Created by scott on 2016/9/6.
 */
public class ClientTest {

	class Terminal extends ITerminal {
		public Terminal(){
			super();
		}

		@Override
		public void onMessage(String message, RpcContext ctx) {
			System.out.println("on Message,msg:" + message + " from server!");
		}

	}

	ServerProxy prxServer = null;
	ITerminalGatewayServerProxy prxGateway = null;


	public ClientTest(){
		prxServer = ServerProxy.create("127.0.0.1",12002,false);
		prxGateway = ITerminalGatewayServerProxy.createWithProxy(prxServer); //
	}

	void call_twoway() throws Exception{
		String ret = prxServer.echo("Hello World!");
		RpcCommunicator.instance().getLogger().debug( ret );
	}


	void call_oneway() throws Exception {
		prxServer.heartbeat_oneway("keepalive",null);
	}

	void call_timeout() throws Exception{
		prxServer.timeout(3,5,null);
	}

	void call_async() throws  Exception{
		prxServer.echo_async("Hello Moto!",new Server_AsyncCallBack(){
			@Override
			public void echo(String result, RpcProxyBase proxy, Object cookie) {
				RpcCommunicator.instance().getLogger().debug(result);
			}
		});
	}

	void call_bidirection() throws Exception{
		prxServer.bidirection_oneway(null);
	}

	void do_test(){
		try{
			call_twoway();
			call_oneway();
			call_timeout();
			call_async();
			call_bidirection();
		}catch(Exception e){
			System.out.println(e.toString());
		}
	}



	void run(){
		System.out.println("Tce Test start..");
		tce.RpcAdapter adapter =  tce.RpcCommunicator.instance().createAdapterWithProxy("local", prxServer);
		Terminal servant = new Terminal();
		adapter.addServant(servant);

		do_test();

	}
}
