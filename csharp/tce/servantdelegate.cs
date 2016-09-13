
using System;

namespace Tce {

    public class RpcServantDelegate {
        public RpcAdapter adapter;
        public int ifidx;

        public virtual RpcMessage invoke(RpcMessage m) {
            return null;
        }
    }

    


}