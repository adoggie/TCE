package tcelib
{
	import flash.utils.ByteArray;
	
	import tcelib.utils.HashMap;

	public class RpcExtraData{
		private var _props:HashMap = new HashMap();
		
		public function RpcExtraData()
		{
			
		}
		
		public function marshall(bytes:ByteArray):uint{
			bytes.writeUnsignedInt(_props.getKeys().length);
			var keys:Array = _props.getKeys();
			var count:uint = 4;
			for (var n:uint=0;n<keys.length;n++){
				var name:String = keys[n] as String;
				var value:String = _props.getKey(name) as String;
				var bs:ByteArray = new ByteArray();
				bs.writeUTFBytes(name);
				count+=8 + bs.length;
				bytes.writeUnsignedInt(bs.length);
				bytes.writeBytes(bs);
				bs.clear();
				bs.writeUTFBytes(value);
				bytes.writeUnsignedInt(bs.length);
				bytes.writeBytes(bs);
				count+= bs.length;
			}
			
			return count;
		}
		
		public function unmarshall(bytes:ByteArray):Boolean{
			var r:Boolean = false;
			var count:uint = 4; 
			var num:uint = bytes.readUnsignedInt();
			var size:uint = 0;
			var key:String;
			var value:String;
			for(var n:uint=0;n<num;n++){
				size = bytes.readUnsignedInt();
				key = bytes.readUTFBytes(size);
				size = bytes.readUnsignedInt();
				value = bytes.readUTFBytes(size);
				_props.put(key,value);
			}
			return r ;
		}
		
	}
}