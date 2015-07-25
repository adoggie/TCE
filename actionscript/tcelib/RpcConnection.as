/**
 * 
 * connection会产生没有return回馈消息，这些消息被堆积在本地，导致内存泄露
 * 需要提供定时回收这些没有反馈的原始消息对象 
 * 
 * 
 */

package tcelib{
	//import NetConnection;
	
	import flash.events.*;
	import flash.net.NetConnection;
	import flash.net.Socket;
	import flash.utils.ByteArray;
	import flash.utils.Endian;
	
	import tcelib.RpcCommAdapter;
	import tcelib.RpcCommunicator;
	import tcelib.RpcConnectionEvent;
	import tcelib.RpcConsts;
	import tcelib.RpcMessage;
	import tcelib.utils.HashMap;
	
	[Event(name="rpcConnected",type="RpcConnectionEvent")]
	[Event(name="rpcDisconnected",type="RpcConnectionEvent")]
	
	public class RpcConnection extends EventDispatcher{
		public var conn:flash.net.NetConnection = null;
		public var delta:Object = null;
		public var _rpcmsglist:HashMap = new HashMap();
		public var id:uint = 0 ;
		public var _adapter:RpcCommAdapter = null;
		private var _sock:Socket = null;
		private var _host:String="";
		private var _port:uint = 0 ;
		private var _packsize:uint = 0;
		private var _buf:ByteArray = new ByteArray();
		private var _msgcached:Array = new Array();
		private var _self:RpcConnection;
		private var _connected:Boolean = false;
		
		public function RpcConnection(){			
			_buf.endian = Endian.BIG_ENDIAN;
			_self = this;
		}
		
		public function connect():void{
			if(_connected == false){
				_sock = new Socket();
				_sock.addEventListener(Event.CLOSE,_onclosed);
				_sock.addEventListener(Event.CONNECT,_onconnected);
				_sock.addEventListener(IOErrorEvent.IO_ERROR,_onerror);
				_sock.addEventListener(SecurityErrorEvent.SECURITY_ERROR,_onerror);
				_sock.addEventListener(ProgressEvent.SOCKET_DATA,_ondata);				
				_sock.endian = Endian.BIG_ENDIAN;
				_sock.connect(_host,_port);
			}
		}
		
		private function reset():void{
			_msgcached = new Array();
			_buf = new ByteArray();
			_rpcmsglist = new HashMap();
			_packsize = 0;
			_sock = null;
		}
		
		// size 不包含magic 4字节
		private function _ondata(e:ProgressEvent):void{
			//var b:ByteArray ;
			var compress:uint ;
			var encrypt:uint;
			var version:uint;
			var r:Boolean;
			
			var d:ByteArray = new ByteArray();
			if(_sock.bytesAvailable>0){
				_sock.readBytes(d);
				_buf.writeBytes(d);	
				_buf.position = 0;
			}
			
			var len:uint;
			len = _buf.length;
			
			while(_buf.bytesAvailable >= _packsize){
				if( _packsize == 0){
					if( _buf.bytesAvailable < 14){
						d = new ByteArray();
						d.writeBytes(_buf,_buf.position,_buf.bytesAvailable);
						_buf = d;
						break;  // too short not enough for headsize
					}
					var magic:uint = _buf.readUnsignedInt();
					_packsize = _buf.readUnsignedInt();	
					compress = _buf.readUnsignedByte();
					encrypt = _buf.readUnsignedByte();
					version = _buf.readUnsignedInt();
					len-=14;
					_packsize-=10;
					if(_packsize<=0){
						_sock.close();
						break;
					}
				}
				if(_buf.bytesAvailable < _packsize){
					d = new ByteArray();
					d.writeBytes(_buf,_buf.position,_buf.bytesAvailable);
					_buf = d;
					break; // less than one packet size					
				}
				var s:String ; //= b.readUTFBytes(_packsize);
				var bytes:ByteArray = new ByteArray();
				//	s = _sock.readUTFBytes(_packsize);
				
				bytes.writeBytes(_buf,_buf.position,_packsize);
				d = new ByteArray();
				d.writeBytes(_buf,_buf.position+_packsize,_buf.bytesAvailable-_packsize);
				_buf = d;
				//_buf.readBytes(bytes,_buf.position,_packsize);
				if( compress ==  1){
					bytes.uncompress();
				}
				_packsize = 0;
				r = decodeMsg(bytes);
				
			}				
		}
		
		private function decodeMsg(bytes:ByteArray):Boolean{
			var m:RpcMessage;
			bytes.position = 0;
			m = RpcMessage.unmarshall(bytes);
			if ( m ==  null){
				return false;
			}
			if( m.calltype & RpcMessage.CALL){
				if( _adapter!=null){
					_adapter.dispatchMsg(m,this as RpcConnection);
				}
			}
			if (m.calltype& RpcMessage.RETURN_){
				doReturnMsg(m);
			}
			return true;
		}

		
		private function _onerror(e:Event):void{
			trace(e.toString());
			reset();
			_connected = false;
			
		}
		
		private function _onclosed(e:Event):void{
			onDisconnected();
			_connected = false;
		}
		
		//socket connected dgw succ！
		//连接上dgw之后重新发送aoids列表
		private function _onconnected(e:Event):void{
			//this.dispatchEvent( new ActiveObjectChannelEvent(ActiveObjectChannelEvent.CHANNEL_OPENED,this));
			trace("socket with destination has connected!");
			onConnected();
		}		

		
		public function attachAdapter(adapter:RpcCommAdapter):void{
			_adapter = adapter;
		}
		
		public function onConnected():void{
//			_buf = new ByteArray();
//			this.dispatchEvent( new RpcConnectionEvent( RpcConnectionEvent.CONNECTED,this) );
			//将缓冲的消息包发出去
			_connected = true;
			for( var n:uint=0;n< _msgcached.length;n++){
				var m:RpcMessage = _msgcached[n] as RpcMessage;
				var r:Boolean;
				r = sendMessage(m);
				if(!r){
					break;
				}
			}
			_msgcached = new Array();
		}
		
		public function onDisconnected():void{
//			this.dispatchEvent( new RpcConnectionEvent( RpcConnectionEvent.DISCONNECTED,this) );
//			this.rpcmsglist.clear();
			reset();
		}
		
		
		public function open(host:String,port:uint):Boolean{
			_host = host;
			_port = port;
			return true;
		}
		
		public function close():void{
			if(_sock != null){
				_sock.close();				
			}
			reset();
		}
		
		public function sendMessage(m:RpcMessage):Boolean{
			var r:Boolean = false;
			var bytes:ByteArray; 
			m.issuetime = new Date().time /1000; 		//记录发送时间			
			m.sequence = tcelib.RpcCommunicator.instance().generateSeq();
			_rpcmsglist.put(m.sequence,m);
			
			if( _connected == false){
				_msgcached.push(m);
				connect();
				return true;
			}			
			
			try{
				r = true;
				_sock.writeUnsignedInt(0xEFD2BB99);
				var compress:uint = 0;
				var ver:uint = 0x101;
				bytes = m.marshall();
				if(compress){				
					bytes.compress();
				}
				var size:uint;
				size = bytes.length + 10; 		// not include magic field
				_sock.writeUnsignedInt(size);
				_sock.writeByte(compress);
				_sock.writeByte(0);
				_sock.writeUnsignedInt(ver);
				_sock.writeBytes(bytes);
				_sock.flush();
			}catch( e:Error){
				r = false
			}
			return r;
		}
		
		public function doReturnMsg(m2:RpcMessage):void{
			if( _rpcmsglist.containsKey(m2.sequence) ){
				var m1:RpcMessage;
				m1 = _rpcmsglist.getValue(m2.sequence) as RpcMessage;
				if( m1.async != null){
					m1.asyncparser(m1,m2);
				}
			}
		}
		
		
		
		//回收掉发送等待未归的消息请求，默认等待300s
		//as为单线程，无需数据保护
		public function garbageCollect():void{
			var keys:Array = _rpcmsglist.getKeys();
			var hash:HashMap = new HashMap();
			for(var n:int=0;n<keys.length;n++){
				var m:RpcMessage = _rpcmsglist.getValue(keys[n]) as RpcMessage;
				var now:Date = new Date();
				if( now.time/1000 - m.issuetime > 300){
					
				}else{
					hash.put( keys[n],m);
				}
			}
			_rpcmsglist.clear();
			_rpcmsglist = hash;
		}
		
		
	}
	
	
}