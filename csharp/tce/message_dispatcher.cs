
using System;
using System.Collections.Generic;
using System.Threading;

namespace Tce {

    public class RpcMessageDispatcher
    {
        public abstract class Client
        {
            private string _name;

            public Client(string name)
            {
                _name = name;
            }

            public string getName()
            {
                return _name;
            }
        }

        private int _threadNum = 1;
        private List<RpcMessage> _messages = new List<RpcMessage>();     //待处理消息队列
        private List<Thread> _threads = new List<Thread>();
        private AutoResetEvent _read_ev = new AutoResetEvent(false);
        private bool _running = false;
        private Client _client;
        public RpcMessageDispatcher(Client client, int thread_num = 1)
        {
            _client = client;
            _threadNum = thread_num;
        }

        public bool open()
        {
            _running = true;
            // 1. create threads 
            if (_threadNum > 0)
            {
                for (int n = 0; n < _threadNum; n++)
                {
                    ThreadStart threadDelegate = new ThreadStart(this.threadMessageProcess);
                    Thread thread = new Thread(threadDelegate);
                    thread.Start();
                    _threads.Add(thread);
                }
            }

            return true;
        }

        public void close()
        {
            _running = false;
            _read_ev.Set();
        }

        /**
        * 处理线程一次取走当前队列中所有消息，并批处理执行
        */
        private void threadMessageProcess()
        {
            while (_running)
            {
                _read_ev.WaitOne();
                List<RpcMessage> msglist;
                lock (_messages)
                {
                    msglist = _messages;
                    _messages = new List<RpcMessage>();
                }
                if (msglist != null)
                {
                    foreach (RpcMessage message in msglist)
                    {
                        message.conn.dispatchMsg(message);  //分派到connection对象处理
                    }
                }
            }
            RpcCommunicator.instance().logger.debug(string.Format("thread  of dispatcher({0}) exiting .. ", _client.getName()));
        }

        public void join()
        {
            // wait for shutdown 
            foreach (var thread in _threads)
            {
                thread.Join();
            }
        }

        public void  dispatchMsg(RpcMessage m) {
            lock (_messages) {
                _messages.Add(m);
                _read_ev.Set();
            }
        }

    }

}