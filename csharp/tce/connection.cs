
using System;
using System.Collections.Generic;

namespace Tce {


    /**
     * RpcConnection 表示任意通信方式的对外和对内方式的通信连接。 
     * 一般移动互联网场景下的客户端，主要通过对外建立与服务器的连接进行交互。
     * 处于服务器侧的adapter一般会打开本地连接(accept)来处理到达客户的连接请求。 
     * 
     */
    public class RpcConnection {
        RpcAdapter  _adapter;
        Dictionary<int, RpcMessage> _messages = new Dictionary<int, RpcMessage>();
        string      _host;
        int         _port;
        int         _type;
        private RpcEndpoint _ep;
        bool        _connected = false;
        string      _token;
        RpcConnectionAcceptor _acceptor;


        protected RpcConnection(RpcAdapter adapter = null) {
            this.adapter = adapter;
            RpcCommunicator.instance().registerConnection(this);
        }

        ~RpcConnection() {
            RpcCommunicator.instance().unregisterConnection(this);
        }

        public RpcConnectionAcceptor acceptor {
            get {
                return _acceptor;
            }
            set { _acceptor = value; }
        }

        public bool isConnected {
            get { return _connected; }
        }

        public RpcAdapter adapter {
            get{ return _adapter;}
            set { _adapter = value; }
        }

        public virtual void open() {
            
        }

        public virtual void close() {
            
        }

        protected virtual void run() {
            
        }

        protected virtual void onMessage(RpcMessage m) {
            if ( _adapter == null &&_acceptor != null && _acceptor.adapter!=null) { // the connection from acceptor
                _adapter = _acceptor.adapter;
            } 
            if (_adapter != null &&  _adapter.dispatcher!=null) { //由adapter的线程执行
                _adapter.dispatcher.dispatchMsg(m);
            }
            else { //由全局通信器进行调度执行
                RpcCommunicator.instance().dispatchMsg(m); 
            }
        }

        protected  virtual  void onError() {
            
        }

        protected  virtual void join() {
            // wait for shutdown。。
        }

        protected virtual void onConnected() {
            _connected = true;
        }

        protected virtual void onDisconnected() {
            _connected = false;
        }

        public virtual bool sendMessage(RpcMessage m) {
            if( (m.calltype&RpcMessage.CALL)!=0 && (m.calltype&RpcMessage.ONEWAY) == 0 ){
                m.conn = this;
                //请求 Communicator 进行调度
                RpcCommunicator.instance().enqueueMessage(m.sequence, m);
            }
            bool r = false;
            lock (this) {
                r = sendDetail(m);
            }
            if (!r){ //发送失败，清除队列消息
                if ((m.calltype & RpcMessage.CALL) != 0 && (m.calltype & RpcMessage.ONEWAY) == 0){
                    RpcCommunicator.instance().dequeueMessage(m.sequence);
                }
            }
            return r;

        }

        protected virtual bool sendDetail(RpcMessage m) {
            return false;
        }


        protected   virtual  void doReturnMsg(RpcMessage m2){
		    RpcMessage m1 = null;
		   // count+=1;

		    m1 = RpcCommunicator.instance().dequeueMessage(m2.sequence);

		    if(m1!=null){
			    if(m1.async !=null){
				    m1.async.callReturn(m1,m2); 
			    }else{
				    lock(m1){
					    m1.result = m2; // assing to init-caller
					    //m1.notify();
				        m1.ev.Set();
				    }
			    }
		    }
	    }
       
       // static int count = 0;

        public void dispatchMsg(RpcMessage m){
            if ((m.calltype & RpcMessage.CALL) != 0){
                if (_adapter != null){
                    _adapter.dispatchMsg(m);
                }
            }
            if ((m.calltype & RpcMessage.RETURN) != 0){
                this.doReturnMsg(m);
            }
        }

        public void setToken(String token){
            _token = token;
        }

    }

}