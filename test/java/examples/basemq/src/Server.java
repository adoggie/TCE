//package test;


import tce.*;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import tce.mq.RpcConnection_QpidMQ;
import tce.utils.ParameterValueSet;
import test.*;
import org.ho.yaml.*;

public class Server {

	static Server handle = null;
	public static Server instance(){
		if(handle == null){
			handle = new Server();
		}
		return handle;
	}

	Server init(){
		return this;
	}


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
				Thread.sleep( secs.intValue() *1000);
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
			String mq_name = ctx.msg.extra.getPropertyValue(RpcConsts.EXTRA_DATA_MQ_RETURN);
			String user_id = ctx.msg.extra.getPropertyValue(RpcConsts.EXTRA_DATA_USER_ID);
			RpcConnection conn = RpcConnection_QpidMQ.getConnection( mq_name );
			ITerminalProxy proxy = new ITerminalProxy(conn);

			ParameterValueSet pset = new ParameterValueSet();
			pset.addParameter(RpcConsts.EXTRA_DATA_MQ_RETURN, mq_name);
			pset.addParameter(RpcConsts.EXTRA_DATA_USER_ID,user_id);
			try{
				proxy.onMessage_oneway("server push message..",pset.data());
			}catch (Exception e){
				System.out.print(e.toString());
			}
		}
	}

	void call_gateway_server(){
		//		prxTerm = new ITerminalProxy(client);
		RpcConnection conn = tce.mq.RpcConnection_QpidMQ.getConnection("mq_gateway");
		ITerminalGatewayServerProxy  prx = new ITerminalGatewayServerProxy( conn );
		try{
			prx.ping();
		}catch (Exception e){
			e.printStackTrace();
			System.out.println(e.toString());
		}
	}

	void run(){
		HashMap<String,String> props = new HashMap<String, String>();
		props.put(RpcCommunicator.INITIALIZE_PROP_THREAD_NUM,"3");

		RpcCommunicator.instance().init("server",props);
		RpcConnection_QpidMQ.initMQEndpoints(RpcCommunicator.instance().getServerName(), "./config.yml");
		tce.RpcCommAdapter adapter = RpcCommunicator.instance().createAdapter("server");

		String BROKER;
		BROKER="amqp://guest:guest@test/?brokerlist='tcp://centos66:5672?retries='2'&connectdelay='1000''";
		BROKER="amqp://guest:guest@test/?brokerlist='tcp://centos66:5672'";



		RpcConnection_QpidMQ server = RpcConnection_QpidMQ.getConnection("mq_server");
		ServantServerImpl servant = new ServantServerImpl();
		adapter.addServant(servant);
		server.attachAdapter(adapter);

		call_gateway_server();

		System.out.println("Server Started!");
		RpcCommunicator.instance().waitForShutdown();
	}


	public boolean initMQEndpoints(String ymlfile){
		try{
			File file = new File(ymlfile);
			if( !file.exists() ){
				return false;
			}
			Object obj = Yaml.load( file );


		}catch (Exception e){
			System.out.print(e.toString());
		}
		return true;
	}

	@SuppressWarnings("unchecked")
	public static void main(String[] args) {
		Server.instance().init().run();
	}
}
