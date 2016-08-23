

using System;
using System.Collections.Generic;
using System.Dynamic;
using System.Threading;

namespace Tce {

   

    class RpcCommunicator:RpcMessageDispatcher.Client {

        public class Settings {
            public string name;     // server name 
            public int threadNum = 1; // 默认启动 1 条处理线程
        }

        private int _sequence = 0;
        private Dictionary<string, RpcAdapter> _adapters;
        private static RpcCommunicator _handle;
        private List<RpcMessage> _pendingMsgList;

        private RpcMessageDispatcher _dispatcher;
        private Dictionary<int, RpcMessage> _cachedMsgList;

        RpcCommunicator() : base("communicator") {
            
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

        public bool initialize(Settings settings) {
            _dispatcher =new RpcMessageDispatcher(this,settings.threadNum);

            return true;
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
            _dispatcher.close();
            _dispatcher.join();
            foreach (KeyValuePair<string, RpcAdapter> kv in _adapters) {
                kv.Value.close();
            }
        }


    }


}