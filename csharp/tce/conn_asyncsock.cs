﻿

using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace Tce {

    class RpcConnectionAsyncSocket : RpcConnectionSocket {
        enum ConnectStatus {
            STOPPED,
            CONNECTING
        }
       

        private List<RpcMessage> _unsent_msglist = new List<RpcMessage>();
        ConnectStatus _status = ConnectStatus.STOPPED;

        private byte[] _bytes = new byte[1024];
        private MemoryStream _stream ;

        public RpcConnectionAsyncSocket(RpcEndpointSocket ep) : base(ep) {
            
        }

        public RpcConnectionAsyncSocket(string host, int port, bool ssl)
            : this(new RpcEndpointSocket(host, port, ssl)){
         
        }

        protected override void onDisconnected() {
            base.onDisconnected();
            _unsent_msglist.Clear();
            _status = ConnectStatus.STOPPED;
        }

        protected override void onConnected() {
            base.onConnected();
            //send all msg in unsent_msglist 
            sendBufferredMsg();
            //start recieve data 
            _stream = new MemoryStream();
            _sock.BeginReceive(_bytes, 0, _bytes.Length, SocketFlags.None, dataRecieve, this);
        }

        private void dataRecieve(IAsyncResult ar) {

            try {
                int recv_size = _sock.EndReceive(ar);
                if (recv_size > 0) {
                    _stream.Seek(0, SeekOrigin.End);
                    _stream.Write(_bytes,0,recv_size);

                    List<MemoryStream> streamlist = new List<MemoryStream>();
                    _stream.Seek(0, SeekOrigin.Begin);
                    ReturnValue rv = parsePacket(_stream);
                    if (rv.code == ReturnValue.DATA_DIRTY)
                    {
                        this.close(); // destroy the socket , connection be lost.
                        RpcCommunicator.instance().logger.debug("data dirty, break out");
                        onDisconnected();
                        return;
                    }

                    BinaryReader reader = new BinaryReader(_stream);
                    byte[] remains = reader.ReadBytes((int)(_stream.Length - _stream.Position));
                    _stream = new MemoryStream();
                    _stream.Write(remains, 0, remains.Length);
                    // left bytes be picked out .
                    foreach (RpcMessage m in rv.msglist){
                        this.onMessage(m);
                    }
                    _sock.BeginReceive(_bytes, 0, _bytes.Length, SocketFlags.None, dataRecieve, this);

                }else {
                    // socket lost
                    onDisconnected();                    
                }
            }
            catch (Exception e) {
                RpcCommunicator.instance().logger.debug("socket connection lost:"+e.ToString());
                onDisconnected();
            }
        }

        protected  override bool connect() {
            IPAddress addr = IPAddress.Parse(_ep.host);
            IPEndPoint ep = new IPEndPoint(addr, _ep.port);

            _status = ConnectStatus.CONNECTING;
            _sock = newSocket();
            _sock.BeginConnect(ep, delegate(IAsyncResult  ar) {

                RpcConnectionAsyncSocket s = (RpcConnectionAsyncSocket)ar.AsyncState;
                try {
                    s.handler.EndConnect(ar);
                    if (s.handler.Connected == true) {
                        s.onConnected();
                        //s._thread = new Thread(run);
                        //s._thread.Start();  // launch one thread for data recieving .
                    }
                }
                catch (Exception e) {
                    // connect failed
                    //s.onDisconnected();
                    RpcCommunicator.instance().logger.error("connect to host failed!");
                }
                //connect failed, trigger event to user as Promise
                if (s.handler.Connected == false) {
                    foreach (RpcMessage m in _unsent_msglist) {
                        RpcAsyncContext ctx = m.async.ctx;
                        ctx.exception = new RpcException(RpcException.RPCERROR_CONNECT_FAILED);
                        m.async.promise.onError(ctx);
                    }
                    _unsent_msglist.Clear();
                }
                s._status = ConnectStatus.STOPPED;
            }, this);
            
            return true;
        }

        protected override bool sendDetail(RpcMessage m) {
            _unsent_msglist.Add(m);
            if (!isConnected) {                
                if (_status == ConnectStatus.STOPPED) {
                    connect();
                }
                return true;
            }
            sendBufferredMsg();
            return true;
        }

        protected bool sendBufferredMsg() {
            if (_unsent_msglist.Count == 0) {
                return true;
            }
            RpcMessage m = _unsent_msglist[0];
            _unsent_msglist.RemoveAt(0);

            if (_sent_num == 0)
            { //第一次连接进入之后的第一个数据包需要携带令牌和设备标识码，用于接入服务器的验证
                if (_token != null && !_token.Equals(""))
                {
                    m.extra.setPropertyValue("__token__", _token);
                    m.extra.setPropertyValue("__device_id__", RpcCommunicator.getSystemDeviceID());
                }
            }

            byte[] bytes = createMsgBody(m).ToArray();

            _sock.BeginSend(bytes, 0, bytes.Length, SocketFlags.None, delegate(IAsyncResult ar) {
                try {
                    RpcConnectionAsyncSocket s = (RpcConnectionAsyncSocket) ar.AsyncState;
                    s.sendBufferredMsg();
                }
                catch (Exception e) {
                    RpcCommunicator.instance().logger.error("BeginSend failed:" + e.ToString());
                }
            }, this);
            
            _sent_num++;
            return true;
        }
    }

}