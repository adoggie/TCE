
// -- coding:utf-8 --
//---------------------------------
//  TCE
//  Tiny Communication Engine
//
//  sw2us.com copyright @2012
//  bin.zhang@sw2us.com / qq:24509826
//---------------------------------

	

function BaseServerProxy(){
	this.conn = null;
	this.delta =null;
	
	this.destroy = function(){
		try{
			this.conn.close();
		}catch(e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}		
	}	;	
	
	this.datetime_async = function(async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 0;
		m.opidx		= 0;
		error		= arguments[1]?arguments[1]:null;
		m.onerror	= error;
		props		= arguments[2]?arguments[2]:null;
		m.extra		= props;
		cookie 		= arguments[3]?arguments[3]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 0;
		try{
			var size =0;
			var _bf_1 = new ArrayBuffer(size);
			var _view = new DataView(_bf_1);
			var _pos=0;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.AsyncCallBack = function(m1,m2){
		var array = new Uint8Array(m2.paramstream);
		var view = new DataView(array.buffer);
		var pos=0;
		if(m1.opidx == 0){
			var _b_2 = '';
			var _sb_3 = view.getUint32(pos);
			pos+=4;
			_b_2 = view.buffer.slice(pos,pos+_sb_3);
			// this var is Uint8Array,should convert to String!!
			pos+= _sb_3;
			_b_2 = String.fromCharCode.apply(null, _b_2.getBytes());
			_b_2 = utf8to16(_b_2);
			m1.async(_b_2,m1.prx,m1.cookie);
		}		
	}	;	
	
}
BaseServerProxy.create = function(uri){
	var prx = new BaseServerProxy();
	prx.conn = new RpcConnection(uri);
	return prx;
};

BaseServerProxy.createWithProxy = function(proxy){
	var prx = new BaseServerProxy();
	prx.conn = proxy.conn;
	return prx;
};


// class BaseServer
function BaseServer(){
	//# -- INTERFACE -- 
	this.delegate = new BaseServer_delegate(this);
	
	//public  datetime(RpcContext ctx){
	this.datetime = function(ctx){
		return '';
	}	;	
}

function BaseServer_delegate(inst) {
	
	this.inst = inst;
	this.ifidx = 0;
	this.invoke = function(m){
		if(m.opidx == 0 ){
			return this.func_0_delegate(m);
		}		
		return false;
	}	;	
	
	this.func_0_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		var cr;
		cr = servant.datetime(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		var mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			var size = 0;
			pos=0;
			var _sb_5 = utf16to8(cr);
			size+= 4 + _sb_5.getBytes().length;
			array = new ArrayBuffer(size);
			view = new DataView(array);
			var _sb_6 = utf16to8(cr).getBytes();
			view.setInt32(pos,_sb_6.length);
			pos+=4;
			var _sb_7 = new Uint8Array(view.buffer);
			_sb_7.set(_sb_6,pos);
			pos += _sb_6.length;
			mr.paramsize = 1;
			mr.paramstream = array;
		}catch(e){
			console.log(e.toString());
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	;	
	
}


function ITerminalGatewayServerProxy(){
	this.conn = null;
	this.delta =null;
	
	this.destroy = function(){
		try{
			this.conn.close();
		}catch(e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}		
	}	;	
	
	this.ping_oneway = function (error,props){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m.ifidx = 1;
		m.opidx = 0;
		m.paramsize = 0;
		error = arguments[0]?arguments[0]:null;
		m.onerror = error;
		props = arguments[1]?arguments[1]:null;
		m.extra=props;
		try{
			var size =0;
			var _bf_8 = new ArrayBuffer(size);
			var _view = new DataView(_bf_8);
			var _pos=0;
			m.prx = this;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RPCERROR_SENDFAILED";
		}		
	}	;	
	
	this.ping_async = function(async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 1;
		m.opidx		= 0;
		error		= arguments[1]?arguments[1]:null;
		m.onerror	= error;
		props		= arguments[2]?arguments[2]:null;
		m.extra		= props;
		cookie 		= arguments[3]?arguments[3]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 0;
		try{
			var size =0;
			var _bf_1 = new ArrayBuffer(size);
			var _view = new DataView(_bf_1);
			var _pos=0;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.AsyncCallBack = function(m1,m2){
		var array = new Uint8Array(m2.paramstream);
		var view = new DataView(array.buffer);
		var pos=0;
		if(m1.opidx == 0){
			m1.async(m1.prx,m1.cookie);
		}		
	}	;	
	
}
ITerminalGatewayServerProxy.create = function(uri){
	var prx = new ITerminalGatewayServerProxy();
	prx.conn = new RpcConnection(uri);
	return prx;
};

ITerminalGatewayServerProxy.createWithProxy = function(proxy){
	var prx = new ITerminalGatewayServerProxy();
	prx.conn = proxy.conn;
	return prx;
};


// class ITerminalGatewayServer
function ITerminalGatewayServer(){
	//# -- INTERFACE -- 
	this.delegate = new ITerminalGatewayServer_delegate(this);
	
	//public  ping(RpcContext ctx){
	this.ping = function(ctx){
	}	
}

function ITerminalGatewayServer_delegate(inst) {
	
	this.inst = inst;
	this.ifidx = 1;
	this.invoke = function(m){
		if(m.opidx == 0 ){
			return this.func_0_delegate(m);
		}		
		return false;
	}	;	
	
	this.func_0_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		servant.ping(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	;	
	
}


function ServerProxy(){
	this.conn = null;
	this.delta =null;
	
	this.destroy = function(){
		try{
			this.conn.close();
		}catch(e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}		
	}	;	
	
	this.echo_async = function(text,async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 2;
		m.opidx		= 0;
		error		= arguments[2]?arguments[2]:null;
		m.onerror	= error;
		props		= arguments[3]?arguments[3]:null;
		m.extra		= props;
		cookie 		= arguments[4]?arguments[4]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 1;
		try{
			var size =0;
			var _sb_1 = utf16to8(text);
			size+= 4 + _sb_1.getBytes().length;
			var _bf_2 = new ArrayBuffer(size);
			var _view = new DataView(_bf_2);
			var _pos=0;
			var _sb_3 = utf16to8(text).getBytes();
			_view.setInt32(_pos,_sb_3.length);
			_pos+=4;
			var _sb_4 = new Uint8Array(_view.buffer);
			_sb_4.set(_sb_3,_pos);
			_pos += _sb_3.length;
			m.paramstream =_bf_2;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.timeout_oneway = function (secs,error,props){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m.ifidx = 2;
		m.opidx = 1;
		m.paramsize = 1;
		error = arguments[1]?arguments[1]:null;
		m.onerror = error;
		props = arguments[2]?arguments[2]:null;
		m.extra=props;
		try{
			var size =0;
			size+= 4;
			var _bf_5 = new ArrayBuffer(size);
			var _view = new DataView(_bf_5);
			var _pos=0;
			_view.setInt32(_pos,secs);
			_pos+=4;
			m.paramstream =_bf_5;
			m.prx = this;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RPCERROR_SENDFAILED";
		}		
	}	;	
	
	this.timeout_async = function(secs,async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 2;
		m.opidx		= 1;
		error		= arguments[2]?arguments[2]:null;
		m.onerror	= error;
		props		= arguments[3]?arguments[3]:null;
		m.extra		= props;
		cookie 		= arguments[4]?arguments[4]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 1;
		try{
			var size =0;
			size+= 4;
			var _bf_1 = new ArrayBuffer(size);
			var _view = new DataView(_bf_1);
			var _pos=0;
			_view.setInt32(_pos,secs);
			_pos+=4;
			m.paramstream =_bf_1;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.heartbeat_oneway = function (hello,error,props){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m.ifidx = 2;
		m.opidx = 2;
		m.paramsize = 1;
		error = arguments[1]?arguments[1]:null;
		m.onerror = error;
		props = arguments[2]?arguments[2]:null;
		m.extra=props;
		try{
			var size =0;
			var _sb_2 = utf16to8(hello);
			size+= 4 + _sb_2.getBytes().length;
			var _bf_3 = new ArrayBuffer(size);
			var _view = new DataView(_bf_3);
			var _pos=0;
			var _sb_4 = utf16to8(hello).getBytes();
			_view.setInt32(_pos,_sb_4.length);
			_pos+=4;
			var _sb_5 = new Uint8Array(_view.buffer);
			_sb_5.set(_sb_4,_pos);
			_pos += _sb_4.length;
			m.paramstream =_bf_3;
			m.prx = this;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RPCERROR_SENDFAILED";
		}		
	}	;	
	
	this.heartbeat_async = function(hello,async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 2;
		m.opidx		= 2;
		error		= arguments[2]?arguments[2]:null;
		m.onerror	= error;
		props		= arguments[3]?arguments[3]:null;
		m.extra		= props;
		cookie 		= arguments[4]?arguments[4]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 1;
		try{
			var size =0;
			var _sb_1 = utf16to8(hello);
			size+= 4 + _sb_1.getBytes().length;
			var _bf_2 = new ArrayBuffer(size);
			var _view = new DataView(_bf_2);
			var _pos=0;
			var _sb_3 = utf16to8(hello).getBytes();
			_view.setInt32(_pos,_sb_3.length);
			_pos+=4;
			var _sb_4 = new Uint8Array(_view.buffer);
			_sb_4.set(_sb_3,_pos);
			_pos += _sb_3.length;
			m.paramstream =_bf_2;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.bidirection_oneway = function (error,props){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m.ifidx = 2;
		m.opidx = 3;
		m.paramsize = 0;
		error = arguments[0]?arguments[0]:null;
		m.onerror = error;
		props = arguments[1]?arguments[1]:null;
		m.extra=props;
		try{
			var size =0;
			var _bf_5 = new ArrayBuffer(size);
			var _view = new DataView(_bf_5);
			var _pos=0;
			m.prx = this;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RPCERROR_SENDFAILED";
		}		
	}	;	
	
	this.bidirection_async = function(async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 2;
		m.opidx		= 3;
		error		= arguments[1]?arguments[1]:null;
		m.onerror	= error;
		props		= arguments[2]?arguments[2]:null;
		m.extra		= props;
		cookie 		= arguments[3]?arguments[3]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 0;
		try{
			var size =0;
			var _bf_1 = new ArrayBuffer(size);
			var _view = new DataView(_bf_1);
			var _pos=0;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.AsyncCallBack = function(m1,m2){
		var array = new Uint8Array(m2.paramstream);
		var view = new DataView(array.buffer);
		var pos=0;
		if(m1.opidx == 0){
			var _b_2 = '';
			var _sb_3 = view.getUint32(pos);
			pos+=4;
			_b_2 = view.buffer.slice(pos,pos+_sb_3);
			// this var is Uint8Array,should convert to String!!
			pos+= _sb_3;
			_b_2 = String.fromCharCode.apply(null, _b_2.getBytes());
			_b_2 = utf8to16(_b_2);
			m1.async(_b_2,m1.prx,m1.cookie);
		}		
		if(m1.opidx == 1){
			m1.async(m1.prx,m1.cookie);
		}		
		if(m1.opidx == 2){
			m1.async(m1.prx,m1.cookie);
		}		
		if(m1.opidx == 3){
			m1.async(m1.prx,m1.cookie);
		}		
	}	;	
	
}
ServerProxy.create = function(uri){
	var prx = new ServerProxy();
	prx.conn = new RpcConnection(uri);
	return prx;
};

ServerProxy.createWithProxy = function(proxy){
	var prx = new ServerProxy();
	prx.conn = proxy.conn;
	return prx;
};


// class Server
function Server(){
	//# -- INTERFACE -- 
	this.delegate = new Server_delegate(this);
	
	//public  echo(text,RpcContext ctx){
	this.echo = function(text,ctx){
		return '';
	}	;	
	
	//public  timeout(secs,RpcContext ctx){
	this.timeout = function(secs,ctx){
	}	
	
	//public  heartbeat(hello,RpcContext ctx){
	this.heartbeat = function(hello,ctx){
	}	
	
	//public  bidirection(RpcContext ctx){
	this.bidirection = function(ctx){
	}	
}

function Server_delegate(inst) {
	
	this.inst = inst;
	this.ifidx = 2;
	this.invoke = function(m){
		if(m.opidx == 0 ){
			return this.func_0_delegate(m);
		}		
		if(m.opidx == 1 ){
			return this.func_1_delegate(m);
		}		
		if(m.opidx == 2 ){
			return this.func_2_delegate(m);
		}		
		if(m.opidx == 3 ){
			return this.func_3_delegate(m);
		}		
		return false;
	}	;	
	
	this.func_0_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		array = new Uint8Array(m.paramstream);
		view = new DataView(array.buffer);
		var text;
		var _sb_8 = view.getUint32(pos);
		pos+=4;
		text = view.buffer.slice(pos,pos+_sb_8);
		// this var is Uint8Array,should convert to String!!
		pos+= _sb_8;
		text = String.fromCharCode.apply(null, text.getBytes());
		text = utf8to16(text);
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		var cr;
		cr = servant.echo(text,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		var mr = new RpcMessage(RpcMessage.RETURN);
		mr.sequence = m.sequence;
		mr.callmsg = m;
		try{
			var size = 0;
			pos=0;
			var _sb_10 = utf16to8(cr);
			size+= 4 + _sb_10.getBytes().length;
			array = new ArrayBuffer(size);
			view = new DataView(array);
			var _sb_11 = utf16to8(cr).getBytes();
			view.setInt32(pos,_sb_11.length);
			pos+=4;
			var _sb_12 = new Uint8Array(view.buffer);
			_sb_12.set(_sb_11,pos);
			pos += _sb_11.length;
			mr.paramsize = 1;
			mr.paramstream = array;
		}catch(e){
			console.log(e.toString());
			r = false;
			return r;
		}		
		r =m.conn.sendMessage(mr);
		return r;
	}	;	
	
	this.func_1_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		array = new Uint8Array(m.paramstream);
		view = new DataView(array.buffer);
		var secs;
		secs = view.getInt32(pos);
		pos+=4;
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		servant.timeout(secs,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	;	
	
	this.func_2_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		array = new Uint8Array(m.paramstream);
		view = new DataView(array.buffer);
		var hello;
		var _sb_13 = view.getUint32(pos);
		pos+=4;
		hello = view.buffer.slice(pos,pos+_sb_13);
		// this var is Uint8Array,should convert to String!!
		pos+= _sb_13;
		hello = String.fromCharCode.apply(null, hello.getBytes());
		hello = utf8to16(hello);
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		servant.heartbeat(hello,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	;	
	
	this.func_3_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		servant.bidirection(ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	;	
	
}


function ITerminalProxy(){
	this.conn = null;
	this.delta =null;
	
	this.destroy = function(){
		try{
			this.conn.close();
		}catch(e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}		
	}	;	
	
	this.onMessage_oneway = function (message,error,props){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ONEWAY);
		m.ifidx = 3;
		m.opidx = 0;
		m.paramsize = 1;
		error = arguments[1]?arguments[1]:null;
		m.onerror = error;
		props = arguments[2]?arguments[2]:null;
		m.extra=props;
		try{
			var size =0;
			var _sb_15 = utf16to8(message);
			size+= 4 + _sb_15.getBytes().length;
			var _bf_16 = new ArrayBuffer(size);
			var _view = new DataView(_bf_16);
			var _pos=0;
			var _sb_17 = utf16to8(message).getBytes();
			_view.setInt32(_pos,_sb_17.length);
			_pos+=4;
			var _sb_18 = new Uint8Array(_view.buffer);
			_sb_18.set(_sb_17,_pos);
			_pos += _sb_17.length;
			m.paramstream =_bf_16;
			m.prx = this;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RPCERROR_SENDFAILED";
		}		
	}	;	
	
	this.onMessage_async = function(message,async,error,props,cookie){
		var r = false;
		var m = new RpcMessage(RpcMessage.CALL|RpcMessage.ASYNC);
		m.ifidx		= 3;
		m.opidx		= 0;
		error		= arguments[2]?arguments[2]:null;
		m.onerror	= error;
		props		= arguments[3]?arguments[3]:null;
		m.extra		= props;
		cookie 		= arguments[4]?arguments[4]:null;
		m.cookie	= cookie;
		m.extra		= props;
		m.paramsize = 1;
		try{
			var size =0;
			var _sb_1 = utf16to8(message);
			size+= 4 + _sb_1.getBytes().length;
			var _bf_2 = new ArrayBuffer(size);
			var _view = new DataView(_bf_2);
			var _pos=0;
			var _sb_3 = utf16to8(message).getBytes();
			_view.setInt32(_pos,_sb_3.length);
			_pos+=4;
			var _sb_4 = new Uint8Array(_view.buffer);
			_sb_4.set(_sb_3,_pos);
			_pos += _sb_3.length;
			m.paramstream =_bf_2;
			m.prx = this;
			m.async = async;
		}catch(e){
			console.log(e.toString());
			throw "RPCERROR_DATADIRTY";
		}		
		r = this.conn.sendMessage(m);
		if(!r){
			throw "RpcConsts.RPCERROR_SENDFAILED";
		}		
	}	;	
	
	
	this.AsyncCallBack = function(m1,m2){
		var array = new Uint8Array(m2.paramstream);
		var view = new DataView(array.buffer);
		var pos=0;
		if(m1.opidx == 0){
			m1.async(m1.prx,m1.cookie);
		}		
	}	;	
	
}
ITerminalProxy.create = function(uri){
	var prx = new ITerminalProxy();
	prx.conn = new RpcConnection(uri);
	return prx;
};

ITerminalProxy.createWithProxy = function(proxy){
	var prx = new ITerminalProxy();
	prx.conn = proxy.conn;
	return prx;
};


// class ITerminal
function ITerminal(){
	//# -- INTERFACE -- 
	this.delegate = new ITerminal_delegate(this);
	
	//public  onMessage(message,RpcContext ctx){
	this.onMessage = function(message,ctx){
	}	
}

function ITerminal_delegate(inst) {
	
	this.inst = inst;
	this.ifidx = 3;
	this.invoke = function(m){
		if(m.opidx == 0 ){
			return this.func_0_delegate(m);
		}		
		return false;
	}	;	
	
	this.func_0_delegate = function(m){
		var r = false;
		var pos =0;
		var array = null;
		var view = null;
		array = new Uint8Array(m.paramstream);
		view = new DataView(array.buffer);
		var message;
		var _sb_6 = view.getUint32(pos);
		pos+=4;
		message = view.buffer.slice(pos,pos+_sb_6);
		// this var is Uint8Array,should convert to String!!
		pos+= _sb_6;
		message = String.fromCharCode.apply(null, message.getBytes());
		message = utf8to16(message);
		var servant = this.inst;
		var ctx = new RpcContext();
		ctx.msg = m;
		servant.onMessage(message,ctx);
		if( (m.calltype & RpcMessage.ONEWAY) !=0 ){
			return true;
		}		
		
		return r;
	}	;	
	
}

