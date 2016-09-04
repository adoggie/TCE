

namespace Tce
{
    /**
     * listen and accept 
     * 处理本地连接进入
     */
    public class RpcConnectionAcceptor
    {
        protected RpcEndpoint _ep;
        private bool _is_open = false;
        private RpcAdapter _adapter = null;

        protected RpcConnectionAcceptor()
        {

        }

        public RpcAdapter adapter
        {
            get
            {
                return _adapter;
            }
            set { _adapter = value; }
        }

        //public virtual bool create(RpcEndpoint ep ) {
        //    return false;
        //}
        public virtual bool open()
        {

            return false;
        }

        public virtual void close()
        {

        }

        public bool isOpen
        {
            get
            {
                return _is_open;
            }
            set { _is_open = value; }
        }


    }

}