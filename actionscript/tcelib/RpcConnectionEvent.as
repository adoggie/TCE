
package tcelib{
	import tcelib.RpcConnection;
	import flash.events.Event;
	
	public class RpcConnectionEvent  extends Event
	{
		public function RpcConnectionEvent(evt:String,conn:RpcConnection)
		{
			super(evt);
			this.conn = conn;
			
		}
		public var data:Object;
		public var conn:RpcConnection;		
		public static const CONNECTED:String ="rpcConnected";
		public static const DISCONNECTED:String ="rpcDisconnected"
	}
}