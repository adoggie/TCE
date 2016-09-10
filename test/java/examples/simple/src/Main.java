



public class Main {
	static ClientTest client = null;
	static ServerTest server = null;
	public static void main(String[] args) {
		tce.RpcCommunicator.instance().init( "test",null);
//		client = new ClientTest();
		//client.run();
		server = new ServerTest();

		server.run();
		tce.RpcCommunicator.instance().waitForShutdown();
	}

}
