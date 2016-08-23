
using System;
using System.IO;
using System.Threading;

namespace Tce {

    class RpcMessage {

        public const int CALL = 0x01;
        public const int RETURN = 0x02;
        public const int TWOWAY = 0x10;
        public const int ONEWAY  = 0x20;
        public const int ASYNC   = 0x40;
        


        public const int RPC_PACKET_HDR_SIZE = 17;

        public int type = RpcConstValue.MSGTYPE_RPC;
        public int sequence = 0;
        public int calltype = 0;
        public int ifidx = 0;
        public int opidx = 0;
        public int errcode = RpcError.RPCERROR_SUCC;
        public int call_id = 0;
        public int paramsize = 0;
        public byte[] paramstream = null;
        public RpcExtraData extra = new RpcExtraData();
        public RpcProxyBase prx = null;
        public long timeout;
        public long issuetime;
        public RpcAsyncCallBackBase async = null;


        public RpcConnection conn;
        public RpcMessage callmsg;
        public object cookie;
        public int status;  // 0 means to send
        public RpcMessage result;
        internal AutoResetEvent ev = new AutoResetEvent(false);


        public static RpcMessage unmarshall(Stream stream){
            RpcMessage m = new RpcMessage();            
            BinaryReader reader = new BinaryReader(stream);
            return m;
        }

        public Stream marshall() {
            // to be continue.. 
            return null;
        }
    }



    class RpcAsyncCallBackBase{
        public object delta = null;
        private string _token = null;
        private bool _execInMainThread = false;

        public void callReturn(RpcMessage m1, RpcMessage m2){

        }

        public void onError(int errorcode){

        }


       

    }


}