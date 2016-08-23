
using System;

namespace Tce {


    // adapter socket , 用于侦听本地socket连接进入
    public class RpcAdapterSocket
    {
        public RpcConnectionAcceptorSocket createAcceptor(RpcEndpointSocket ep)
        {
            RpcConnectionAcceptorSocket acceptor = new RpcConnectionAcceptorSocket();

            if (acceptor.create(ep))
            {
                return acceptor;
            }
            return null;
        }
    }
}