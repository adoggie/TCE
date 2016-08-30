using System;

namespace Tce {
    public class RpcException : Exception {
        public int error;
        public string errmsg;
        public RpcException(int error, string errmsg="") {
            this.error = error;
            this.errmsg = errmsg;
        }

        public override string ToString() {
            return string.Format("error:{0}, message:{1}", this.error, this.errmsg);
        }


        public const int RPCERROR_SUCC = 0;
        public const int RPCERROR_SENDFAILED = 1;
        public const int RPCERROR_DATADIRTY = 3;
        public const int RPCERROR_TIMEOUT = 2;
        public const int RPCERROR_INTERFACE_NOTFOUND = 4;
        public const int RPCERROR_UNSERIALIZE_FAILED = 5;
        public const int RPCERROR_REMOTEMETHOD_EXCEPTION = 6;
        public const int RPCERROR_DATA_INSUFFICIENT = 7;
        public const int RPCERROR_REMOTE_EXCEPTION = 8;
        public const int RPCERROR_CONNECT_UNREACHABLE = 101;
        public const int RPCERROR_CONNECT_FAILED = 102;
        public const int RPCERROR_CONNECT_REJECT = 103;
        public const int RPCERROR_CONNECTION_LOST = 104;
        public const int RPCERROR_INTERNAL_EXCEPTION = 105;

        public static string errorString(int err) {
            string str = "";
            if (err == RPCERROR_SUCC) str = "RPCERROR_SUCC";
            else if (err == RPCERROR_SENDFAILED) str = "RPCERROR_SENDFAILED";
            else if (err == RPCERROR_DATADIRTY) str = "RPCERROR_DATADIRTY";
            else if (err == RPCERROR_TIMEOUT) str = "RPCERROR_TIMEOUT";
            else if (err == RPCERROR_INTERFACE_NOTFOUND) str = "RPCERROR_INTERFACE_NOTFOUND";
            else if (err == RPCERROR_UNSERIALIZE_FAILED) str = "RPCERROR_UNSERIALIZE_FAILED";
            else if (err == RPCERROR_REMOTEMETHOD_EXCEPTION) str = "RPCERROR_REMOTEMETHOD_EXCEPTION";
            else if (err == RPCERROR_DATA_INSUFFICIENT) str = "RPCERROR_DATA_INSUFFICIENT";
            else if (err == RPCERROR_REMOTE_EXCEPTION) str = "RPCERROR_REMOTE_EXCEPTION";
            else if (err == RPCERROR_CONNECT_UNREACHABLE) str = "RPCERROR_CONNECT_UNREACHABLE";
            else if (err == RPCERROR_CONNECT_FAILED) str = "RPCERROR_CONNECT_FAILED";
            else if (err == RPCERROR_CONNECT_REJECT) str = "RPCERROR_CONNECT_REJECT";
            else if (err == RPCERROR_CONNECTION_LOST) str = "RPCERROR_CONNECTION_LOST";
            else if (err == RPCERROR_INTERNAL_EXCEPTION) str = "RPCERROR_INTERNAL_EXCEPTION";
            return str;
        }
    }

}