
using  System;

namespace Tce {
    public class RpcEndpoint {
        
    }

    public class RpcEndpointSocket:RpcEndpoint {
        public string host;
        public int port;
        public bool ssl = false;
    }
}