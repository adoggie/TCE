
package tcelib{
	
	//import RpcConsts;
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	
	import tcelib.RpcConsts;
	
	public class RpcMessage{
		public static const CALL:uint = 0x01;
		public static const RETURN_:uint = 0x02;
		public static const CALL_TWO_WAY:uint = 0x00;
		public static const CALL_ONE_WAY:uint = 0x10;
		public static const DEFAULT_CALL:uint = CALL | CALL_TWO_WAY;
		public static const ONEWAY_CALL:uint = CALL | CALL_ONE_WAY;
		
		public var params:Array = new Array();
		public var type:int = RpcConsts.MSGTYPE_RPC;
		public var sequence:uint =0;
		public var calltype:int = RpcMessage.DEFAULT_CALL;
		public var ifidx:uint = 0;
		public var opidx:uint = 0;
		public var errcode:int = RpcConsts.RPCERROR_SUCC;
		public var extra:RpcExtraData = new RpcExtraData();		
		public var paramsize:int = 0; //消息内部存在多少参数
		public var call_id:uint = 0;
		
		public var paramstream:ByteArray = null;
		public var prx:Object = null;
		public var async:Function = null;
		public var asyncparser:Function = null;
		public var issuetime:Number = 0; //发送时间
		
		
		
		public function RpcMessage(){
		}
		
		public function addParam(p:ByteArray):void{
			this.params.push(p);
		}
		
		public function marshall():ByteArray{
			var stream:ByteArray = new ByteArray();
			stream.endian = Endian.BIG_ENDIAN;
			stream.writeByte( this.type);
			stream.writeUnsignedInt(this.sequence);
			stream.writeByte(calltype);
			stream.writeShort( ifidx );
			stream.writeShort(this.opidx);
			stream.writeInt(this.errcode);
			stream.writeByte(this.params.length);
			stream.writeShort(this.call_id);
			extra.marshall(stream);
			
			for(var n:int=0; n< this.params.length; n++){
				var bytes:ByteArray = this.params[n] as ByteArray;
				stream.writeBytes(bytes);
			}
			
			return stream;
		}
		
		public static function unmarshall(d:ByteArray):RpcMessage{
			var m:RpcMessage = null ;
			
			try{
				m = new RpcMessage();
				m.type = d.readUnsignedByte();
				m.sequence = d.readUnsignedInt();
				m.calltype = d.readUnsignedByte();
				m.ifidx = d.readUnsignedShort();
				m.opidx = d.readUnsignedShort();
				m.errcode = d.readInt();
				m.paramsize = d.readUnsignedByte(); //参数个数
				m.call_id = d.readUnsignedShort();
				m.extra.unmarshall(d);
				m.paramstream = new ByteArray();
				m.paramstream.writeBytes(d,d.position,d.bytesAvailable);
				m.paramstream.position = 0;
				return m;				
			}catch(e:Error){
				trace(e.toString());
			}
			return null;
			//return m;
			
		}
		
		
	}

}