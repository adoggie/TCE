

namespace Tce {
    /**
     * listen and accept 
     * 处理本地连接进入
     * acceptor产生的connection读写数据需采用io异步机制
     */
    public class RpcConnectionAcceptorSocket : RpcConnectionAcceptor
    {
        private RpcEndpointSocket _ep;
        RpcConnectionAcceptorSocket(RpcEndpointSocket ep)
        {
            _ep = ep;
        }

        //目前adapter仅仅处理client端，server模式暂不提供，故不会有Accptor的存在
        public static RpcConnectionAcceptorSocket create(RpcEndpointSocket ep)
        {
            RpcConnectionAcceptorSocket acceptor = new RpcConnectionAcceptorSocket(ep);
            return acceptor;
        }

        public override bool open()
        {
            base.open();
            return true;
        }

        public override void close()
        {

        }


    }

}