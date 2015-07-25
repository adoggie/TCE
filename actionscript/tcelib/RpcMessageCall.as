package tcelib{
	import tcelib.RpcConsts;
	import tcelib.RpcMessage;
	
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	import tcelib.RpcCommunicator
	
	public class RpcMessageCall extends RpcMessage{
		
		public function RpcMessageCall(){
			sequence = RpcCommunicator.instance().generateSeq();		
		}
		
	}
}