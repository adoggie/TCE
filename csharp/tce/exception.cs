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
    }

}