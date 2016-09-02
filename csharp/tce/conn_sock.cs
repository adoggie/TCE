
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace Tce {

    class RpcConnectionSocket : RpcConnection {
        public const int META_PACKET_HDR_SIZE = 14;
        public const uint PACKET_META_MAGIC = 0xEFD2BB99;
        public const int VERSION = 0x00000100;
        public const int MAX_PACKET_SIZE = 1024*1024*1;

        private Thread _thread;
        private bool _ssl = false;
        private RpcEndpointSocket _ep;
        private string _token;

        private Socket _sock = null;
        private long _sent_num = 0;

        public RpcConnectionSocket(RpcEndpointSocket ep) {
            _ep = ep;
        }

        /*
            c++ : constructor invoke other constructor 
            class Test{    
               Test() {
                   new (this) Test(1); 
               }
               Test(int){}
            }
         */

        public RpcConnectionSocket(string host, int port, bool ssl)
            : this(new RpcEndpointSocket(host, port, ssl)){
         
        }

        public override void open() {
            
        }

        public override void close() {
            base.close();
            if (_sock != null) {
                _sock.Close();
            }
            _sock = null;
        }

        bool connect() {
            bool r = false;
            IPAddress addr = IPAddress.Parse(_ep.host);
            try {
                _sock = newSocket();
                _sock.Connect( new IPEndPoint(addr,_ep.port)); // it should be non-blocked, add in later.
                _thread = new Thread( run);
                _thread.Start();  // launch one thread for data recieving .
                r = true;
            }
            catch {
                _sock = null;               
            }
            return r;
        }

        private Socket newSocket(){
            Socket sock = null ;
            if (_ep.ssl) {
                //todo. next ssl
                
            }
            else {
                sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            }

            return sock;
        }

        protected override void onDisconnected() {
            close();
        }

        protected override bool sendDetail(RpcMessage m) {
            
            if (_sock == null) {
                if (!connect()) {
                    return false;
                }
            }
            if (_sent_num == 0) { //第一次连接进入之后的第一个数据包需要携带令牌和设备标识码，用于接入服务器的验证
                if (_token != null && !_token.Equals("")) {
                    m.extra.setPropertyValue("__token__",_token);
                    m.extra.setPropertyValue("__device_id__", RpcCommunicator.getSystemDeviceID());
                }
            }

            byte[] body = null;
            body = ((MemoryStream) m.marshall()).ToArray();
            byte[] hdr = createMetaPacketHeader(body.Length);
            _sock.Send(hdr);
            _sock.Send(body);
            _sent_num++;

            return true;
        }

        private byte[] createMetaPacketHeader(int msg_size) {
            byte[] hdrbBytes = null;
            MemoryStream stream =new MemoryStream();
            BinaryWriter writer =new BinaryWriter(stream);
            unchecked {
                writer.Write((uint)IPAddress.HostToNetworkOrder((int)PACKET_META_MAGIC));    
            }
            
            writer.Write((uint)IPAddress.HostToNetworkOrder(msg_size + META_PACKET_HDR_SIZE-4));
            writer.Write((byte)RpcConstValue.COMPRESS_NONE);
            writer.Write((byte)RpcConstValue.ENCRYPT_NONE);
            writer.Write((uint)IPAddress.HostToNetworkOrder(VERSION) );
            hdrbBytes = stream.ToArray();
            return hdrbBytes;
        }

        class ReturnValue {
            public const int DATA_DIRTY = -1;
            public const int NEED_MORE = 0;
            public const int SUCC = 1;

            public int code = DATA_DIRTY; // -1 : data is dirty ; 0 - need more data 
            public int size = 0;
            public List<RpcMessage> msglist;
            public MemoryStream remain;

            public ReturnValue(int code,List<RpcMessage> msglist, MemoryStream remain = null) {
                this.code = code;
                //this.size = size;
                this.remain = remain;
                this.msglist = msglist;
            }
        }

        private ReturnValue parsePacket(MemoryStream stream) {
            /***
             *  magic,packet_size,compress,encrypt,version,content
             *  packet_size: all fields size except magic.
             * 
             */
            List<RpcMessage> msglist = new List<RpcMessage>();
            BinaryReader reader = new BinaryReader(stream);
            long size = stream.Length ;
            while (size > 0) {
                if (size < META_PACKET_HDR_SIZE) {
                    return new ReturnValue(ReturnValue.NEED_MORE, msglist, stream);                    
                }
                uint magic = (uint)IPAddress.NetworkToHostOrder(reader.ReadInt32());
                uint pktsize = (uint) IPAddress.NetworkToHostOrder(reader.ReadInt32());
                byte compress = reader.ReadByte();
                byte encrypt = reader.ReadByte();
                uint version = (uint) IPAddress.NetworkToHostOrder(reader.ReadInt32());
                if (magic != PACKET_META_MAGIC) {
                    return new ReturnValue(ReturnValue.DATA_DIRTY, msglist, stream);
                }
                if (pktsize > MAX_PACKET_SIZE) {
                    return new ReturnValue(ReturnValue.DATA_DIRTY, msglist, stream);
                }
                if (size <= META_PACKET_HDR_SIZE - 4) {
                    return new ReturnValue(ReturnValue.DATA_DIRTY, msglist, stream);
                }
                if (size < pktsize + 4) {
                    return new ReturnValue(ReturnValue.NEED_MORE, msglist, stream);
                }
                size -= META_PACKET_HDR_SIZE;
                uint content_size = pktsize - (META_PACKET_HDR_SIZE - 4);
                Stream s = new MemoryStream(reader.ReadBytes((int) content_size));
                size -= content_size;

                //decompress stream 
                if (compress == RpcConstValue.COMPRESS_ZLIB) {
                    s = new DeflateStream(s,CompressionMode.Decompress);
                }else if (compress == RpcConstValue.COMPRESS_BZIP2) {
                    // nothing.
                }

                RpcMessage m = RpcMessage.unmarshall(s);
                if (m == null) {
                    return new ReturnValue(ReturnValue.DATA_DIRTY, msglist, stream);
                }
                m.conn = this;
                msglist.Add(m);
            }
            return new ReturnValue(ReturnValue.SUCC,msglist,stream);
        }

        protected override  void run() {
            //接收数据
            long recv_num = 0;
            byte[] bytes = new byte[1024];
            MemoryStream stream = new MemoryStream();
            RpcCommunicator.instance().logger.debug("thread of connection come in..");
            try {
                this.onConnected();
                while (true) {
                    int size = _sock.Receive(bytes);
                    if (size > 0) {
                        stream.Seek(0, SeekOrigin.End);
                        stream.Write(bytes, 0, size);
                    }
                    else {
                        break;
                    }
                    List<MemoryStream> streamlist = new List<MemoryStream>();
                    stream.Seek(0, SeekOrigin.Begin);
                    ReturnValue rv = parsePacket(stream);
                    if (rv.code == ReturnValue.DATA_DIRTY) {
                        this.close(); // destroy the socket , connection be lost.
                        RpcCommunicator.instance().logger.debug("data dirty, break out");
                        break;
                    }

                    BinaryReader reader = new BinaryReader(stream);
                    stream = new MemoryStream(reader.ReadBytes( (int)(stream.Length - stream.Position))); 
                        // left bytes be picked out .
                    foreach (RpcMessage m in rv.msglist) {
                        this.onMessage(m);
                    }
                }

            }
            catch (Exception e) {
                RpcCommunicator.instance().logger.debug(e.ToString());
            }

            onDisconnected();
            RpcCommunicator.instance().logger.debug("thread of connection leaving..");
        }
    }

}