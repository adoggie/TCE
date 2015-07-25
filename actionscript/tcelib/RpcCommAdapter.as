
package tcelib{
	
	//import tcelib.NetConnection;
	import flash.net.NetConnection;
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	
	import tcelib.RpcConnection;
	import tcelib.RpcConsts;
	import tcelib.RpcContext;
	import tcelib.RpcMessage;
	import tcelib.RpcServant;
	import tcelib.RpcServantDelegate;
	import tcelib.utils.HashMap;

	public class RpcCommAdapter{
		
		public var servants:HashMap = new HashMap();
		public var id:String;
		public var conns:HashMap = new HashMap();
		
		public function RpcCommAdapter(){
			
		}
		
		public function addServant(servant:RpcServant):void{
			this.servants.put(servant.delegate.index,servant.delegate);
		}
		
		public function doError(errcode:int,m:RpcMessage,conn:RpcConnection):void{
			var sm:RpcMessageReturn = new RpcMessageReturn();
			sm.sequence = m.sequence;
			sm.errcode = errcode;
			conn.sendMessage(sm);
		}
		
		
		public function dispatchMsg(m:RpcMessage,conn:RpcConnection):void{
			if( m.calltype & RpcMessage.CALL){
				if(! servants.containsKey(m.ifidx)){
					doError(RpcConsts.RPCERROR_INTERFACE_NOTFOUND,m,conn);
					return;
				}
				var dg:RpcServantDelegate;
				dg = servants.getValue(m.ifidx)  as RpcServantDelegate;
				if(! dg.optlist.containsKey( m.opidx ) ){
					doError(RpcConsts.RPCERROR_INTERFACE_NOTFOUND,m,conn);
					return;
				}
				var func:Function;
				func = dg.optlist.getValue(m.opidx) as Function;
				var ctx:RpcContext = new RpcContext();
				
				ctx.conn = conn;
				
				ctx.msg = m;
				try{
					func( ctx );
				}catch(e:Error){
					doError(RpcConsts.RPCERROR_REMOTEMETHOD_EXCEPTION,m,conn)
					return;
				}
			}
			/*
			if( m.calltype & RpcMessage.RETURN_){
				conn.doReturnMsg(m);
			}*/
			
		}
		
	}
	
}