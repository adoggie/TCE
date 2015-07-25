

package tcelib{
	
	import flash.events.*;
	import flash.utils.Timer;

	
	public class RpcCommunicator{
		private static var _handle:RpcCommunicator = null;
		private var _seq:uint = 0;
		private var _timer:Timer;
		private var _conns:Vector.<RpcConnection> = new Vector.<RpcConnection>();
		
		public function RpcCommunicator(){
			_timer = new Timer(300*1000); // five minutes for GC
			_timer.addEventListener(TimerEvent.TIMER,ontimer);

		}
		
		public static function instance():RpcCommunicator{
			if(_handle == null){
				_handle = new RpcCommunicator();
			}
			return _handle;
				
		}
		
		public function generateSeq():uint{
			return ++_seq;
		}
		
		//garbage collect
		private function ontimer(e:TimerEvent):void{
			trace('garbage collection executing..');
			for(var n:uint = 0;n< _conns.length;n++){
				_conns[n].garbageCollect();
			}
		}
		
		protected function registerConnection(conn:RpcConnection):void{
			_conns.push( conn );
		}
		
		protected function unRegisterConnection(conn:RpcConnection):void{
			for(var n:uint = 0;n< _conns.length;n++){
				if( conn == _conns[n]){
					_conns.splice(n,1);
					break;
				}
			}
		}

		
	}
		
}