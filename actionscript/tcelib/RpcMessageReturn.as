package tcelib{
	
	import tcelib.RpcConsts;
	import tcelib.RpcMessage;
	
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	import tcelib.RpcCommunicator
	
	public class RpcMessageReturn extends RpcMessage{
		
		public function RpcMessageReturn(){
			calltype = RpcMessage.RETURN_;
		}
		
	}
}