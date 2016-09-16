

using System;
using System.Collections.Generic;
using System.Threading;
using Timer = System.Timers.Timer;

namespace Tce {

    class RpcCommunicator:RpcMessageDispatcher.Client {

        public class Settings {
            public string name ="";     // server name 
            public int threadNum = 1; // 默认启动 1 条处理线程
            public int callwait = 1000*30; //最大调用返回等待超时时间,触发 promise.error
            public int checkHealthInterval = 1000*3;
            public bool socket_async_conn = true;
        }

        private int _sequence = 0;
        private Dictionary<string, RpcAdapter> _adapters = new Dictionary<string, RpcAdapter>();
        private static RpcCommunicator _handle;
        private List<RpcMessage> _pendingMsgList = new List<RpcMessage>();

        private RpcMessageDispatcher _dispatcher;
        private Dictionary<int, RpcMessage> _cachedMsgList = new Dictionary<int, RpcMessage>();
        private Settings _settings = new Settings();
        private List<RpcConnection> _conns = new List<RpcConnection>();

        private Timer _timer;

        RpcCommunicator() : base("communicator") {
            
        }

        public Settings settings{
            get { return _settings; }
        }

        public static string getSystemDeviceID() {
            return "id_xxx";
        }

        public static RpcCommunicator instance() {            
            if (RpcCommunicator._handle == null) {
                RpcCommunicator._handle = new RpcCommunicator();
            }
            return RpcCommunicator._handle;
        }

        public bool initialize(string name,Settings settings=null) {
            if (settings != null) {
                _settings = settings;
            }
            _dispatcher =new RpcMessageDispatcher(this,_settings.threadNum);
            _dispatcher.open();

            _timer = new Timer(this.settings.checkHealthInterval);
            _timer.Elapsed += new System.Timers.ElapsedEventHandler(_timerCheckHealth);
            _timer.AutoReset = true;
            _timer.Enabled = true;
            
            return true;

        }

        protected void _timerCheckHealth(object source, System.Timers.ElapsedEventArgs e) {
            //RpcCommunicator.instance().logger.debug("Communicator:: health checking..");
            List<RpcMessage> removeList = new List<RpcMessage>();
            lock (_cachedMsgList){
                long cursec = Utility.unixTimestamp(DateTime.Now);
                List<int> deprecatedlist=new List<int>();                
                foreach (KeyValuePair<int, RpcMessage> kv in _cachedMsgList) {
                    if ( (cursec - kv.Value.issuetime)*1000 > _settings.callwait) {
                        deprecatedlist.Add( kv.Key);
                    }
                }
                foreach (int seq in deprecatedlist) {
                    removeList.Add( _cachedMsgList[seq]);
                    _cachedMsgList.Remove(seq);
                    RpcCommunicator.instance().logger.error(String.Format("message({0}) be dropped for timeout", seq));
                }               
            }
            //
            foreach (RpcMessage message in removeList) {
                if (message.async.promise == null) {
                    message.async.onError(RpcException.RPCERROR_TIMEOUT);
                }
                else {
                    RpcAsyncContext ctx = new RpcAsyncContext();
                    ctx.promise = message.async.promise;
                    ctx.exception = new RpcException(RpcException.RPCERROR_TIMEOUT);
                    message.async.promise.onError(ctx);
                }
            }

        }  

        public int getUniqueSequence() {
            Interlocked.CompareExchange(ref _sequence, Int32.MaxValue - 0xffff, 0);
            Interlocked.Increment(ref _sequence);
            return _sequence;
        }

        public RpcLogger logger {
            get {
                return RpcLogger.instance();
            }
        }

        /**
         * 将接收到的Rpc消息推入处理队列，等待线程读取
         * 
         */
        internal RpcCommunicator enqueueMessage(int sequence, RpcMessage m){
            lock (_cachedMsgList) {
                m.issuetime = Utility.unixTimestamp(DateTime.Now);
                _cachedMsgList.Add(sequence,m);
            }
            return this;
            
        }

        internal RpcMessage dequeueMessage(int sequence) {
            RpcMessage m = null;
            lock (_cachedMsgList) {
                if (_cachedMsgList.ContainsKey(sequence)) {
                    m = _cachedMsgList[sequence];
                }
                _cachedMsgList.Remove(sequence);
            }
            return m;            
        }
        
        //消息进入communicator调度执行
        internal void dispatchMsg(RpcMessage m) {
            _dispatcher.dispatchMsg(m);
        }

        public void waitForShutdown() {
           
            _dispatcher.join();
            foreach (KeyValuePair<string, RpcAdapter> kv in _adapters) {
                kv.Value.join();
                kv.Value.close();
            }
        }

        public void shutdown() {
            lock (_conns) {
                foreach (RpcConnection conn in _conns) {
                    conn.close();
                }
            }
            _dispatcher.close();
            foreach (KeyValuePair<string, RpcAdapter> kv in _adapters){                
                kv.Value.close();
            }
        }

        public RpcAdapter createAdapterWithProxy(String id, RpcProxyBase proxy){
            RpcAdapter adapter = null;
            adapter = new RpcAdapter(id);
            proxy.conn.adapter = adapter;
            //		adapter.addConnection(proxy.conn);
            addAdatper(adapter);
            return adapter;
        }

        public void addAdatper(RpcAdapter adapter){
            if (_adapters.ContainsKey(adapter.id)){
                return;
            }
            _adapters.Add(adapter.id, adapter);
        }

        public RpcAdapter createAdapter(string id){
            RpcAdapter adapter = new RpcAdapter(id);
            addAdatper(adapter);
            return adapter;
        }

        public RpcConnection createConnection(int type, string host, int port){
            if ((type & RpcConstValue.CONNECTION_SOCK) != 0)
            {
                if (_settings.socket_async_conn) {
                    return new RpcConnectionAsyncSocket(host, port, (type & RpcConstValue.CONNECTION_SSL) != 0);
                }
                return new RpcConnectionSocket(host, port, (type & RpcConstValue.CONNECTION_SSL) != 0);
            }
            return null;
        }

        public RpcLogger getLogger() {
            return this.logger;
        }


        public int getProperty_DefaultCallWaitTime(){
            return  _settings.callwait;
        }

        public  void registerConnection(RpcConnection conn) {
            lock (_conns) {
                if (!_conns.Contains(conn)) {
                    _conns.Add(conn);
                }
            }
        }

        public void unregisterConnection(RpcConnection conn) {
            lock (_conns) {
                _conns.Remove(conn);
            }
        }
	
    }


}