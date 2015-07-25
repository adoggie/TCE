String.prototype.getBytes = function () {
	var bytes = [];
	for (var i = 0; i < this.length; ++i) {
		bytes.push(this.charCodeAt(i));
	}
	return bytes;
};


ArrayBuffer.prototype.getBytes = function () {
	var bytes = [];
	var buf = new DataView(this);
	for (var i = 0; i < buf.byteLength  ; ++i) {
		bytes.push(buf.getUint8(i));
	}
	return bytes;
};

ArrayBuffer.prototype.concat = function ( buf2) {
//	var newbuf = new ArrayBuffer( );
	var bytearray = new Uint8Array(this.byteLength + buf2.byteLength);
	bytearray.set( new Uint8Array(this));
	bytearray.set(new Uint8Array(buf2),this.byteLength);
	return bytearray.buffer;
};

//-----------------------------------------------
function RpcLogger(){
    this.debug = function(msg){};
    this.error = function(msg){};
}

function RpcConsts(){

}
RpcConsts.MSGTYPE_RPC   = 1;
RpcConsts.RPCERROR_SUCC = 0;
RpcConsts.COMPRESS_NONE = 0;
RpcConsts.COMPRESS_ZLIB = 1;



function RpcMessage(calltype){
	this.type = RpcConsts.MSGTYPE_RPC;
	this.sequence = RpcCommunicator.instance().getSequence();
	this.calltype = calltype;
	this.ifidx = 0;
	this.opidx = 0;
	this.errcode = 0;
	this.call_id = 0;
	this.paramsize = 0;
	this.paramstream = new ArrayBuffer();
	this.extra = {};// new Object();

	this.prx    = null;
	this.async  = null;
	this.conn   = null;
	this.callmsg = null;
	this.onerror = null;        // prototype -  void onerror(){}
    this.cookie = null;       // user callback

	this.marshall = function(){
		try{
			var size =  17  ; // fixed size
			if(this.paramstream !=null){
				size+=this.paramstream.byteLength ;
			}
			size+=4;  // extr hdr size
			var extrsize= size;
			var keynum = 0;
			if(this.extra!=null){
//				size+=4; // how many items in dict
				var name = null;
                var value = null;
                var keys = Object.getOwnPropertyNames(this.extra);
                for( var n=0;n<keys.length;n++){
				    name = keys[n];
                    value = String(this.extra[name])
					size+= 4 + name.getBytes().length;
					size+= 4 + value.getBytes().length;
					keynum+=1;
				}
			}
			extrsize = size - extrsize; // content size
			// end size calculation
			var view = new DataView(new ArrayBuffer(size));
			var bytebuf = new Uint8Array(view.buffer);
			var pos =0;
			view.setUint8(pos,this.type); pos+=1;
			view.setUint32(pos,this.sequence); pos+=4;
			view.setUint8(pos,this.calltype); pos+=1;
			view.setUint16(pos,this.ifidx); pos+=2;
			view.setUint16(pos,this.opidx); pos+=2;
			view.setInt32(pos,this.errcode); pos+=4;
			view.setUint8(pos,this.paramsize); pos+=1;
			view.setUint16(pos,this.call_id); pos+=2;

			view.setUint32(pos,keynum); pos+=4;
			if(this.extra!=null){
                var name = null;
                var value = null;
                var length = 0 ;
                var keys = Object.getOwnPropertyNames(this.extra);
                for( var n=0;n<keys.length;n++){
                    name = keys[n];
                    value = String(this.extra[name])
                    length = name.getBytes().length
					view.setUint32(pos,length);
					pos+=4;
					bytebuf.set(name.getBytes(),pos);
					pos+=length;
                    length = value.getBytes().length;
					view.setUint32(pos,length);
					pos+=4;
					bytebuf.set(value.getBytes(),pos);
					pos+=length;
				}
			}

			if(this.paramstream !=null){
				var content = new Uint8Array(this.paramstream);
//				console.log(content.byteLength);
				bytebuf.set(content,pos);
			}
			var hdr = this.makeMetaNetPacketHeader(bytebuf.byteLength);
			return [hdr,bytebuf.buffer];
		}catch (e){
			console.log(e);
			return null;
		}
	};
	// end marshall()

	this.makeMetaNetPacketHeader=function(size){
		var view = new DataView(new ArrayBuffer(14));
		var pos = 0;
		view.setUint32(pos,0Xefd2bb99);
        pos+=4;
		view.setUint32(pos,size+10);
        pos+=4;
		view.setUint8(pos,RpcConsts.COMPRESS_NONE);
        pos+=1;
		view.setUint8(pos,0);
        pos+=1;
		view.setUint32(pos,0x0100);
        pos+=4;
		return view.buffer;
	};

	// extra - ArrayBuffer
	this.setExtra = function(extr,keynum){
		var dv = new DataView(extr);
		var pos=0;
		var size = 0;
		for(var n=0;n<keynum;n++){
			var itemsize = dv.getUint32(pos);
			pos+=4;
			var k = extr.slice(pos,pos+itemsize);
			k = String.fromCharCode.apply(null, k.getBytes());
			pos+=itemsize;

			itemsize = dv.getUint32(pos);
			pos+=4;
			var v = extr.slice(pos,pos+itemsize);
			v = String.fromCharCode.apply(null, v.getBytes());
			pos+=itemsize;

			this.extra[k.toString()] = v.toString();
		}
		return pos;
	};
}

// d - ArrayBuffer
RpcMessage.unmarshall=function(d){
	try{
		var m = new RpcMessage();
		var dv = new DataView(d);
		var bytes = new Uint8Array(d);
		var pos = 0;
		m.type = dv.getUint8(pos); pos+=1;
		m.sequence = dv.getUint32(pos); pos+=4;
		m.calltype = dv.getUint8(pos); pos+=1;
		m.ifidx = dv.getUint16(pos); pos+=2;
		m.opidx = dv.getUint16(pos); pos+=2;
		m.errcode = dv.getInt32(pos);  pos+=4;
		m.call_id = dv.getUint16(pos); pos+=2;
		m.paramsize = dv.getUint8(pos); pos+=1;
		var keynum=0;
		keynum = dv.getUint32(pos);  pos+=4;

		var extra = d.slice(pos);
		pos += m.setExtra(extra,keynum);
		m.paramstream = d.slice(pos);
		return m;
	}catch(e){
		return null;
	}
}

RpcMessage.CALL = 0x01;
RpcMessage.RETURN = 0x02;
RpcMessage.TWOWAY = 0x10;
RpcMessage.ONEWAY = 0x20;
RpcMessage.ASYNC = 0X40;


function RpcContext(){
	this.msg = null;
	this.conn = null;
}

function RpcConnection(url){
	this.ws = null;
	this.msglist ={}; // new Object(); // {id:msg,...}
	this.data = new ArrayBuffer(0);
	this.adapter = null;
	this.sendbuf=[];
	var self = this;
	this.connecting = 0;
    this.token = null;
    this.numMsgSent = 0 ;
    this.target_url = null;

    this.setToken =function(token){
        this.token = token;
    };

	this.connect = function(){
		try{
			if(self.ws != null){
				return true;
			}
            self.target_url = url;
			self.ws = new WebSocket(url);
			self.ws.onmessage = self.onMessage;
			self.ws.onopen = self.onOpen;
			self.ws.onclose = self.onClose;
			self.ws.onerror = self.onError;

		}catch(e){
			self.ws = null;

			return false;
		}
		return true;
	};


	this.onload_rpcdata = function(e){
		var d = e.target.result; 			// d - ArrayBuffer
		self.data = self.data.concat(d); //
		var blocks = [];
		var rc;
		rc = self.parseMsg(blocks);
		for(var n=0;n<blocks.length;n++){
			var b = blocks[n];
			var m = RpcMessage.unmarshall(b);
			if(m!=null){
				m.conn = self;
				self.dispatchMsg(m);
			}
		}
	};

	// meta message parse out
	this.parseMsg = function(blocks){
		var dv = new DataView(self.data);
//		var bytes = new Uint8Array(this.data);

		var pos = 0;
		while(dv.byteLength > 14){
			pos = 0;
			var magic = dv.getUint32(pos);
			pos+=4;
			var pkgsize = dv.getUint32(pos);
			pos+=4;
			var compress = dv.getUint8(pos);
			pos+=1;
			var encrypt = dv.getUint8(pos);
			pos+=1;
			var ver = dv.getUint32(pos);
			pos+=4;
			if( magic != 0xefd2bb99){
				self.close();
				return ;
			}

			if( pkgsize > 1024*1024 ){ // max size limited, 2MB
				self.close();
				return ;
			}
			if( dv.byteLength< pkgsize+4){
				return ; //
			}

			var block = self.data.slice(14,14+pkgsize-10);
			blocks.push(block);
			self.data = self.data.slice(pkgsize+4);
			dv = new DataView(self.data);
		}
	};

	this.onerror_rpcdata = function(e){
		//evt.target.error.name == "NotReadableError"
		console.log('file reader error!');
		console.log(e.toString());
	};

	this.onloadstart_rpcdata = function(e){
		console.log(e.toSource());
	}

	this.onMessage = function(e){
		//e.data - Blob

		var reader = new FileReader();
		reader.onload= self.onload_rpcdata;

		reader.onloadend= function(e){
//			console.log(this.result);
		};
//		reader.onprogress= function(e){
//			console.log(e.toString());
//		};

		reader.onerror = self.onerror_rpcdata;
//		reader.onloadstart = self.onloadstart_rpcdata;

		reader.readAsArrayBuffer(e.data);
	//	reader.readAsBinaryString(e.data);
	};

    this._sendBufferedMessage = function(){

        for(var n=0;n<self.sendbuf.length;n++){
            var m = self.sendbuf[n];
            //var d = new Blob(m.marshall());

            if( self.numMsgSent == 0){
                if(m.extra ==null){
                    var device_id = RpcCommunicator.instance().getDeviceId();
                    if(device_id == null){
                        device_id = "";
                    }
                    if(self.token !=null) {
                        m.extra = {__token__:self.token,__device_id__:device_id};
                    }
                }
            }
            self.numMsgSent+=1;

            var ds = m.marshall();
            if( (m.calltype&RpcMessage.ASYNC)!=0 ){
                self.msglist[ String(m.sequence)] = m;
            }
            for(var x=0;x<ds.length;x++){
                self.ws.send(ds[x]);
            }
        }
        self.sendbuf = [];
    };

	this.onOpen = function(e){
        self._sendBufferedMessage();
//		self.onConnected();
	};

	this.onError = function(e){
        console.log( 'target host:'+ self.target_url +' rejected!' + 'error:'+ e.toString());
		self.close();
        self.resetData();
	};

	this.onClose = function(e){
        self.resetData();
	};

    this.resetData = function(){
        self.msglist ={};// new Object();
        self.sendbuf = [];
        self.ws = null;
        self.numMsgSent = 0 ;
        self.target_url = null;
    };

	this.close = function(e){
		if(self.ws!=null){
			try{
				self.ws.close();
			}catch(e){

			}
			self.ws = null;
		}
	};

//	this.onDisconnected = function(){
//		// clear msg-queue
//		self.ws = null;
//        self.numMsgSent = 0 ;
//	};

//	this.onConnected = function(){
//
//	};

	this.attachAdapter = function(adapter){
		self.adapter = adapter;
	};

	this.isConnected = function(){
		//return this.ws!=null?true:false;
		if( self.ws==null){
			return false;
		}
		if( self.ws.readyState == WebSocket.prototype.OPEN  ){
			return true;
		}

		return false;
	};

	this.sendMessage = function(m){
		try{
			// Blob(x)  - x must be array
			if( self.isConnected() == false){
				self.sendbuf.push(m);
				self.connect();
				return true;
			}

//			var ds = m.marshall();
//			if( (m.calltype&RpcMessage.ASYNC)!=0 ){
//				self.msglist[ String(m.sequence)] = m;
//			}
//			for(var x=0;x<ds.length;x++){
//				self.ws.send(ds[x]);
//			}
            self.sendbuf.push(m);
            self._sendBufferedMessage();

		}catch(e){
			//self.ws = null;
			console.log(e.toString());
			if(m.onerror != null){
				m.onerror();
			}
			return false;
		}
		return true;
	};

	this.doReturnMsg = function(m2){
		var m1 = null;
		if( self.msglist.hasOwnProperty(String(m2.sequence)) ){
			m1 = self.msglist[String(m2.sequence)];
			delete self.msglist[String(m2.sequence)];
		}
		if(m1!=null){
			if(m1.async!=null){
				try{
					m1.prx.AsyncCallBack(m1,m2);
				}catch(e){
					console.log(e.toString());
				}
			}
		}
	};

	this.dispatchMsg = function(m){
		if( (m.calltype&RpcMessage.CALL) !=0){
			if(self.adapter!=null){
				self.adapter.dispatchMsg(m);
			}
		}
		if( (m.calltype&RpcMessage.RETURN) !=0){
			self.doReturnMsg(m);
		}
	};
}

function RpcAdapter(communicator){
	this.communicator = communicator;
	this.servants={};
	var self = this;
	this.addServant=function(servant){
		servant.delegate.inst = servant;
		this.servants[String(servant.delegate.ifidx)] = servant;
	};

	this.dispatchMsg=function(m){
		try{
			if( self.servants.hasOwnProperty(String(m.ifidx)) ){
				servant = self.servants[String(m.ifidx)];
				servant.delegate.invoke(m)
			}
		}catch(e){
			console.log(e.toString());
		}
	};

}


function RpcCommunicator(){
	this.seq = 0;
	this.adapters=[];
    this.logger = null;
    this.device_id = null;
    var self = this;

	this.getSequence = function(){
		return this.seq++;
	};

	this.init = function(){
		//alert('Communicator.init()');
		return true;
	};

    this.getDeviceId = function(){
       return self.device_id;
    };

    this.setDeviceId = function(devid){
        self.device_id = devid;
    };

	this.createAdapter = function(id){
		var adapter = new RpcAdapter(this);
		this.adapters.push(adapter);
		return adapter;
	};

    this.getLogger = function(){
        if(this.logger ==null){
            this.logger = new RpcLogger();
        }
        return this.logger;
    };

    this.setLogger = function(logger){
        this.logger = logger;
    };
}

RpcCommunicator.handle = null;
RpcCommunicator.instance = function(){
	if(RpcCommunicator.handle == null){
		RpcCommunicator.handle = new RpcCommunicator();
	}
	return RpcCommunicator.handle;
};


function utf16to8(str) {
	var out, i, len, c;
	out = "";
    str = String(str);
	len = str.length;
	for(i = 0; i < len; i++) {
		c = str.charCodeAt(i);
		if ((c >= 0x0001) && (c <= 0x007F)) {
			out += str.charAt(i);
		} else if (c > 0x07FF) {
			out += String.fromCharCode(0xE0 | ((c >> 12) & 0x0F));
			out += String.fromCharCode(0x80 | ((c >>  6) & 0x3F));
			out += String.fromCharCode(0x80 | ((c >>  0) & 0x3F));
		} else {
			out += String.fromCharCode(0xC0 | ((c >>  6) & 0x1F));
			out += String.fromCharCode(0x80 | ((c >>  0) & 0x3F));
		}
	}
	return out;
}

function utf8to16(str) {
	var out, i, len, c;
	var char2, char3;

	out = "";
	len = str.length;
	i = 0;
	while(i < len) {
		c = str.charCodeAt(i++);
		switch(c >> 4)
		{
			case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
			// 0xxxxxxx
			out += str.charAt(i-1);
			break;
			case 12: case 13:
			// 110x xxxx   10xx xxxx
			char2 = str.charCodeAt(i++);
			out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
			break;
			case 14:
				// 1110 xxxx  10xx xxxx  10xx xxxx
				char2 = str.charCodeAt(i++);
				char3 = str.charCodeAt(i++);
				out += String.fromCharCode(((c & 0x0F) << 12) |
					((char2 & 0x3F) << 6) |
					((char3 & 0x3F) << 0));
				break;
		}
	}

	return out;
}
