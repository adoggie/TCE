﻿
using System;
using System.Collections.Generic;
using System.Runtime.Remoting.Channels;
using System.Threading;

namespace Tce
{

    /**
     * RpcAdater
     *  adapter 应用于 connection 与 servant的连接，同时可以接驳多路connection和多个服务servant对象，
     *  并且rpc请求的消息分派也在adapter中进行，adapter可以配置成多线程处理。
     * 
     * 
     * adapter 默认不启用处理线程，仅占用communicator的处理线程
     */
    public class RpcAdapter:RpcMessageDispatcher.Client{

        //adapter的参数配置 
        public class Settings {
            public int threadNum = 0; // 默认不启动adapter内处理线程
        }

        private string _id;
        private Dictionary<int, RpcServantDelegate> _servants = new Dictionary<int, RpcServantDelegate>();
        private List<RpcConnection> _conns = new List<RpcConnection>();
        private Settings _settings = new Settings();        
        private List<RpcConnectionAcceptor> _acceptors = new List<RpcConnectionAcceptor>(); //一个adapter中允许打开多种服务接收远端客户请求连接到达
        private RpcMessageDispatcher _dispatcher;

        public string id
        {
            get
            {
                return _id;
            }
            //set { _name = value; }
        }

        public Settings settings {
            get{ return _settings;}
        }

        public RpcAdapter(string id, Settings settings = null):base(id) {
            
            if( settings!=null ){
                _settings = settings;
            }
            _id = id;
        }

        public void addConnectionAcceptor(RpcConnectionAcceptor acceptor) {
            lock (_acceptors) {
                if (!_acceptors.Contains(acceptor)) {
                    acceptor.adapter = this;
                    _acceptors.Add(acceptor);
                }
            }
        }

        public void removeConnectionAcceptor(RpcConnectionAcceptor acceptor) {
            lock (_acceptors) {
                _acceptors.Remove(acceptor);
                acceptor.adapter = null;
            }
        }

        //打开服务接收远端连接进入,可以是真实的本地端点设备，或者是伪设备连接
         //目前adapter仅仅处理client端，server模式暂不提供，故不会有Accptor的存在
        //public T createAcceptor<T,EP>(ref EP ep) where T:RpcConnectionAcceptor,new() {
        //    T acceptor = new T();
            //return acceptor;

        //   if( acceptor.create( ref ep) ){
         //       return acceptor;
         //   }
          //  return null;
       // }

        /**
         *  attachConnection()
         * 添加连接到adapter，连接上传递进入的rpc请求将在本adapter内的所有servant对象上传递
         *  应用于NAT后端的客户app发起与server的连接，并将连接关联到本地adapter，以便实现rpc服务的本地提供
         */
        public RpcAdapter attachConnection(RpcConnection conn) {
            lock (_conns) {
                if (!_conns.Contains(conn)) {
                    _conns.Add(conn);
                    conn.adapter = this;
                }
            }
            return this;
        }

        public void detachConnection(RpcConnection conn) {
            lock (_conns) {
                _conns.Remove(conn);
                conn.adapter = null;
            }
        }

        public RpcAdapter addServant(RpcServant servant) {
            if (!_servants.ContainsKey(servant.delegate_.ifidx)) {
                _servants.Add( servant.delegate_.ifidx,servant.delegate_);
            }
            return this;
        }

        /**
         * 打开本地通信端点，用于接收远程客户连接到达
         *  (server end) 
         */
        //public RpcConnection openEndpoint(RpcEndpoint ep) {

        //    return null;
        //}

        public bool open() {
            bool succ = false;
            if (_settings.threadNum > 0) {
                _dispatcher = new RpcMessageDispatcher(this, _settings.threadNum);
                succ = _dispatcher.open();
            }

            // if acceptor has not opened, then do open. 
            lock (_acceptors) {
                foreach (RpcConnectionAcceptor acceptor in _acceptors) {
                    if (acceptor.isOpen == false) {
                        if (!acceptor.open()) {
                            RpcCommunicator.instance()
                                .logger.error("open connection acctor failed! " + acceptor.ToString());
                        }
                    }
                }                
            }
            return succ;
        }

        public void close() {
            lock (_acceptors) {
                foreach (RpcConnectionAcceptor acceptor in _acceptors) {
                    acceptor.close(); //  it should block thread until it exit exactly.
                    acceptor.adapter = null;
                }
            }
            if (_dispatcher != null) {
                _dispatcher.close();               
            }
        }

        public void join() {
            if (_dispatcher != null){                
                _dispatcher.join();
            }
        }

        public RpcMessageDispatcher dispatcher{
            get {
                return _dispatcher;
            }
        }

        //处理在此adapter内产生的消息
        /*
        public void onConnectionMessage(RpcMessage m) {
            if (_dispatcher != null) {
                _dispatcher.dispatchMsg(m);
            }
        }
         * */

        

        void doError(int errcode, RpcMessage m){
            RpcMessageReturn msgreturn = new RpcMessageReturn(m.sequence,errcode);
            msgreturn.send(m.conn);
            //		RpcConnection conn = m.conn;
            /*
            var sm:RpcMessageReturn = new RpcMessageReturn();
            sm.sequence = m.sequence;
            sm.errcode = errcode;
            conn.sendMessage(sm);
            */
        }

        public void dispatchMsg(RpcMessage m) {
            RpcServantDelegate dg = null;
            if ((m.calltype & RpcMessage.CALL) != 0) {
                lock (_servants) {
                    if (!_servants.ContainsKey(m.ifidx)) {
                        doError( RpcException.RPCERROR_INTERFACE_NOTFOUND,m);
                        return;
                    }
                    dg = _servants[m.ifidx];
                }
                try {
                    RpcMessage msgreturn = dg.invoke(m);
                    if (msgreturn != null) {
                        m.conn.sendMessage(msgreturn);
                    }
                }
                catch (Exception e) {
                    RpcCommunicator.instance().logger.error(" execute servant failed:" + e.ToString());
                    doError(RpcException.RPCERROR_REMOTEMETHOD_EXCEPTION,m);
                }
            }
        }

    }

}