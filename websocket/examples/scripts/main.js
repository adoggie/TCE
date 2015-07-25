CTLocalStorageUtil = function() {
};

CTLocalStorageUtil.prototype = {  

    isSupport : function(){
    	if(('localStorage' in window) && window['localStorage'] !== null){
           return true;
        }
    	else {
    		return false;
    	}
    },
    
    setValue : function(key, value){
    	if(this.isSupport())
    		localStorage.setItem(key,value);
    },
   
    getValue : function(key){    	
    	if(this.isSupport())
    		return localStorage.getItem(key);
    	else
    		return undefined;
    },
    
    remove : function(key){
    	if(this.isSupport())
    		localStorage.removeItem(key);
    },
    
    clear : function() {
    	if(this.isSupport())
    		localStorage.clear();
    }
};

var localStorageUtil = new CTLocalStorageUtil();

var g_token = '';

//g_token='VmSfJN7wXB8MUumjV+aiqpYr1rHZc6Xi28WUrELVjIQr4SwNvZE827/D8s6rEQ1fp3SKWswriloZEyYC5eGVlHTg+jFVaraZhXIPwopCjxzJ4GrXmlhR6DAfyHPP3TC25LbklbhuT0llsBbAR3k+EF+Xm+DlooDtmVlIR8Ld+eGeJAnYOGumFM0HR2/qnlW2V/7BWNnvemCjxCGIBRwBQKW3oEX6btYsTo+TDVlGStgaw7bpZq4c8PsLyNyZg5Cn1z6QvRichADaSE1n3x8VgV5WyQ6OGjE1UiPm+JNlf7eHIw4FCLoV6qBiBLm51MRnm/nb0NrK0vxDKXfoQ2toxQ==';
function getUserToken(){
    return g_token;
};

function validToken() {
	
	g_token = localStorageUtil.getValue("ct_token");
	var user = localStorageUtil.getValue("ct_nickname");
	var password = localStorageUtil.getValue("ct_password");
	console.log('get local:'+g_token+','+user+','+password);
	
	if (null == g_token){
		console.log("no token");
		document.location.href = "signin.html";	
	}
			
	$.ajax({
		type : "POST",
		url : "/CarteamWebAPI/ValidToken",
		cache : false,
		data : {
			token : g_token
		},
		dataType : "json",
		success : function(data) {
			// {"status":"0",'expired':1}
			if (0 == data.status && 0 == data.expired) {
				console.log("login success.");
				console.log(data);
			} else if (0 == data.status && 1 == data.expired) {
				console.log("login token expired.");
				if (null == user || null == password) {
					console.log("no local user/password storage");
					document.location.href = "signin.html";
				}
				refreshToken(user,password);
			} else if (401 == data.status) {
				console.log("login token is not the validation.");
				document.location.href = "signin.html";
			}
		},
		error : function() {
			console.log("valid token error.");
		}
	});
};

function refreshToken(user, password) {
	$.ajax({
		type : "POST",
		url : "/CarteamWebAPI/SignIn",
		cache : false,
		data : {
			nickname : user,
			password : password
		},
		dataType : "json",
		success : function(data) {
			console.log("login success.");
			if (0 == data.status) {
				console.log("get refresh token.");
				console.log(data);

				localStorageUtil.setValue("ct_token", data.token);
				g_token = data.token;
			} else if (401 == data.status) {
				console.log("user name or password is error.");
				document.location.href = "signin.html";
			}
		},
		error : function() {
			console.log("fetch token error.");
			document.location.href = "signin.html";
		}
	});
};


//


function LocationProvider(){
    this.onData = null;
    this.watchId = null;
    var _self = this;
    this.stopped = true;

    this.open = function(){
    	_self.stopped = false;
        setTimeout(_self.getlocation,5000);
        return true;
    };

    this.getlocation =function(){
    	if( _self.stopped){
    		return ;
    	} 
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
        if( _self.onData !=null){
            _self.onData(d);
        }
        setTimeout(_self.getlocation,30000);
    };


    this.locationError = function (poserror){
        console.log("error: "+ poserror.code + " " + poserror.message);
        if( poserror.PERMISSION_DENIED == poserror.code){

        }
        _self.open();
    };


    this.close = function(){
        if( _self.watchId != null){
            navigator.geolocation.clearWatch(_self.watchId);
            _self.watchId = null;
        }
        _self.stopped = true;
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
    this._stopped = true;

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
//        _self._reconnect = true;
        if(_self._stopped){
            return;
        }
        if( _self._connected == false){
            _self.connect();
        }
        if(_self._reconnect == true){
            setTimeout(_self.reconnect,5000);
        }
    };

    this.open = function(){
        _self._reconnect = true;
        _self._stopped = false;
        _self.reconnect();
    };

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
                _self.ws.close();
            }catch(e){
                console.log(e.toString());
            }
            this.ws = null;
        }
        _self._reconnect = false;
        _self._stopped = true;
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
            //_self.data.trim();
            _self._parseMsg(s);
        }catch(e){
            console.log(e.toString());
        }
    };

    // d is Object
    this.send = function(d){
        try{
            _self.ws.send(JSON.stringify(d)+'\n');
        }catch(e){
            console.log(e.toString());
        }
    };

    this.sendBytes = function(d){
        try{
            _self.ws.send(d);
        }catch(e){
            console.log(e.toString());
        }
    };
}

/***
 * @param url       websocket-server address , ws://host:port/path
 * @param token     user-token
 * @param user      userdata-callback
 * @constructor
 */
function MessageReactor(url,token,user){
    var _token = token;
    var _user = user;
    this.ws = null;
    var _self = this;
    var _loc = null;
    this.open= function(){
        _self.ws = new Connection(url);
        _self.ws.onConnected = function(from){
            console.log('connected!');
            _self.ws.send({t:'v',k:_token});
        };
        _self.ws.onDisconnected = function(from){
        };
        _self.ws.onUserMessage = function(msg){
            if(_user!=null){
                _user(msg);
            }
        };
        _self.ws.open();

        _loc = new LocationProvider();
        _loc.open();
        _loc.onData = function(d){
            //_self.ws.send({'type':'gps','lon':d.lon,'lat':d.lat,'time':d.time,'speed':d.speed,'direction':d.heading});
        	//float 5 
            _self.ws.send({t:'g',o:d.lon,a:d.lat,s:d.speed,d:d.heading});
        };
    };
    this.close = function(){
    	try{
	        _self.ws.close();
	        _loc.close();
    	}catch(e){
    		console.log(e.toString());
    	}
    };
}

//////////////////////////////////////////////
// test code
/*
 var dr = new DataReactor("ws://xxx",token,function(msg){});
 */

