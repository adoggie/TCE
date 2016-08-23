
using System;

namespace Tce {

    class RpcServantDelegate {
        public RpcAdapter adapter;
        public int ifidx;

        public virtual bool invoke(RpcMessage m) {
            return true;
        }
    }

    


}