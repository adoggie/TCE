import tce.RpcContext;
import tce.RpcConnection;
import tce.* ;
import test.* ;
import tce.utils.*;
import tce.netty.*;

import java.util.HashMap;

/**
 * Created by scott on 2016/9/6.
 */
public class ServerTest {

	class ServantServerImpl extends test.Server{

		public ServantServerImpl() {
			super();
		}

		@Override
		public String echo(String text, RpcContext ctx) {
			System.out.println("oob data:" + ctx.msg.extra.getProperties().toString());
			System.out.println(text);
			return text;
		}

		@Override
		public void timeout(Integer secs, RpcContext ctx) {
			System.out.print("enter timeout:"+ secs.toString());
			try{
				Thread.sleep( secs *1000);
			}catch (Exception e){
				System.out.print(e.toString());
			}
		}

		@Override
		public void heartbeat(String hello, RpcContext ctx) {
			System.out.print(hello);
		}

		@Override
		public void bidirection(RpcContext ctx) {
//			String mq_name = ctx.msg.extra.getPropertyValue(RpcConsts.EXTRA_DATA_MQ_RETURN);
//			String user_id = ctx.msg.extra.getPropertyValue(RpcConsts.EXTRA_DATA_USER_ID);
//			RpcConnection conn = RpcConnection_QpidMQ.getConnection( mq_name );
//			ITerminalProxy proxy = new ITerminalProxy(conn);
//
//			ParameterValueSet pset = new ParameterValueSet();
//			pset.addParameter(RpcConsts.EXTRA_DATA_MQ_RETURN, mq_name);
//			pset.addParameter(RpcConsts.EXTRA_DATA_USER_ID,user_id);
//			try{
//				proxy.onMessage_oneway("server push message..",pset.data());
//			}catch (Exception e){
//				System.out.print(e.toString());
//			}
		}
	}

	void call_gateway_server(){
		//		prxTerm = new ITerminalProxy(client);
//		RpcConnection conn = tce.mq.RpcConnection_QpidMQ.getConnection("mq_gateway");
//		ITerminalGatewayServerProxy  prx = new ITerminalGatewayServerProxy( conn );
//		try{
//			prx.ping();
//		}catch (Exception e){
//			e.printStackTrace();
//			System.out.println(e.toString());
//		}

	}

	void run(){

		HashMap<String,String> props = new HashMap<String, String>();
		props.put(RpcCommunicator.INITIALIZE_PROP_THREAD_NUM,"3");

		RpcCommunicator.instance().init("server",props);

		RpcAdapter adapter = RpcCommunicator.instance().createAdapter("server");

		RpcConnectionAcceptor_NettySocket acceptor =
				RpcConnectionAcceptor_NettySocket.create( new RpcEndPoint("localhost",16005));
		acceptor.open();
		adapter.addConnectionAcceptor(acceptor);


		ServantServerImpl servant = new ServantServerImpl();
		adapter.addServant(servant);


//		call_gateway_server();

		System.out.println("Server Started!");

	}
}
