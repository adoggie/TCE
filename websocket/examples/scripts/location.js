
String.prototype.trim=function(){
	return this.replace(/(^\s*)(\s*$)/g,'');
};


function LocationProvider(){
	this.onData = null;
	this.watchId = null;
	var _self = this;


	this.open = function(){
		setTimeout(_self.getlocation,5000);

//		if (navigator.geolocation) {
//			this.watchId = navigator.geolocation.watchPosition(this.locationSuccess,this.locationError,
//				{
//					enableHighAcuracy: false,
//					timeout: 10000,
//					maximumAge:5000
//				});
//			console.log( this.watchId);
//		}else{
//			//alert("Your browser does not support Geolocation!");
//			return false;
//		}
		return true;
	};

	this.getlocation =function(){
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition( _self.locationSuccess);
		}
	};

	this.locationSuccess = function(position){
		var d = {'lon':position.coords.longitude,
			'lat':position.coords.latitude,
			'heading':position.coords.heading,
			'speed':position.coords.speed,
			'time':position.timestamp
		};
//		console.log(d.toString());
		//alert(d.toString());
		if( _self.onData !=null){
			_self.onData(d);
		}
		setTimeout(_self.getlocation,5000);
	};


	this.locationError = function (poserror){
		console.log("error: "+ poserror.code + " " + poserror.message);
		if( poserror.PERMISSION_DENIED == poserror.code){

		}
		_self.open();
	};


	this.close = function(){
		if( this.watchId != null){
			navigator.geolocation.clearWatch(this.watchId);
			this.watchId = null;
		}
	};
}

////

function Connection(url){
	this.ws = null;

	this.onUserMessage = null;
	this.data ='';
	this._reconnect = false;
	var _self = this;
	this._connected = false;
	this.onConnected = null;
	this.onDisconnected = null;

	this.connect = function(){
		try{
			_self.data='';
			_self.ws = new WebSocket(url);
			_self.ws.onmessage = _self._onMessage;
			_self.ws.onopen = _self._onOpen;
			_self.ws.onclose = _self._onClose;
			_self.ws.onerror = _self._onError;
		}catch(e){
			console.log(e.toString());
			this.ws = null;
			return false;
		}
		return true;
	};

	this.reconnect = function(){
		_self._reconnect = true;
		if( _self._connected == false){
			_self.connect();
		}
		if(_self._reconnect == true){
			setTimeout(_self.reconnect,5000);
		}
	}


	this._onOpen = function(e){
		console.log('socket connected!');
		_self._connected = true;
		if(_self.onConnected != null){
			_self.onConnected(_self);
		}
	};

	this._onError = function(e){
		_self.close();
		console.log('socket error!');
	};

	this._onClose = function(e){
		console.log('socket lost!');
		_self._connected = false;
		if(_self.onDisconnected != null){
			_self.onDisconnected(_self);
		}
	};

	this.close = function(e){
		if(_self.ws!=null){
			try{
				this.ws.close();
			}catch(e){

			}
			this.ws = null;
		}
	};

	// meta message parse out
	this._parseMsg = function(d){
		obj = JSON.parse(d);
		if( _self.onUserMessage!=null){
			_self.onUserMessage(obj);
		}
	};

	this._onMessage = function(e){
		try{
			console.log('recved bytes:'+ e.data);

			_self.data += e.data;
			var idx = _self.data.indexOf('\n');
			if(idx==-1){
				return ;
			}
			var s = _self.data.substring(0,idx);
			_self.data = _self.data.substring(idx+1);
			_self.data.trim();
			_self._parseMsg(s);
		}catch(e){
			console.log(e.toString());
		}
	};

	// d is Object
	this.send = function(d){
		try{
			console.log(d);
			this.ws.send(JSON.stringify(d)+'\n');
		}catch(e){
			console.log(e.toString());
		}
	};

	this.sendBytes = function(d){
		try{
			this.ws.send(d);
		}catch(e){
			console.log(e.toString());
		}
	};
}

function LocationWrapper(url,token){
	var _token = token;
	this.open= function(){
		ws = new Connection(url);
		ws.onConnected = function(from){
			console.log('connected!');
			ws.send({'type':'verify','token':_token});
		};
		ws.onDisconnected = function(from){
		};
		ws.onUserMessage = function(msg){
		};
		ws.reconnect();

		loc = new LocationProvider();
		loc.open();
		loc.onData = function(d){
			ws.send({'type':'gps','lon':d.lon,'lat':d.lat,'time':d.time,'speed':d.speed,'direction':d.heading});
		};
	};
}

//////////////////////////////////////////////
// test code
/*
function test_code(text){
	ws = new Connection('ws://172.26.181.128:8080/CarteamWebAPI/CarteamWebSocket');
	//ws = new Connection('ws://localhost:8080');
	ws.onConnected = function(from){
		console.log('connected!');
		ws.send({'type':'verify','token':test_token});
		$('#socket').html('connected!');
	};
	ws.onDisconnected = function(from){
		$('#socket').html('lost!');
	};
	ws.onUserMessage = function(msg){
		$('#msg').html(msg.type);
	};

	ws.reconnect();


	loc = new LocationProvider();
	loc.open();
	loc.onData = function(d){
		//console.log(String(d.lat)+" "+ String(d.lon) );
		$('#lonlat').html(String(d.lat) +','+String(d.lon));
		ws.send({'type':'gps','lon':d.lon,'lat':d.lat,'time':d.time,'speed':d.speed,'direction':d.heading});
	};
}


$(document).ready(function() {
	test_code('lonlat');
});


 loc = new LocationWrapper('ws://172.26.181.128:8080/CarteamWebAPI/CarteamWebSocket',test_token);
 loc.open();

*/
