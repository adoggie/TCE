
using System;

namespace Tce {

    public class RpcServantDelegate {
        public RpcAdapter adapter;
        public int ifidx;

        public virtual bool invoke(RpcMessage m) {
            return true;
        }
    }

    


}