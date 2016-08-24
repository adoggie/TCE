
using  System;

namespace Tce {
    public class RpcEndpoint {
        
    }

    public class RpcEndpointSocket:RpcEndpoint {
        public string host;
        public int port;
        public bool ssl = false;

        public RpcEndpointSocket(string host, int port, bool ssl = false) {
            this.host = host;
            this.port = port;
            this.ssl = ssl;
        }
    }
}