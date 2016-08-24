
using System;
using System.Dynamic;

namespace Tce
{

    public class RpcServant {
        private RpcServantDelegate _delegate;

        string _name;

        public RpcServantDelegate delegate_{
            get
            {
                return _delegate;
            }
            set { _delegate = value; }
        }

        public string name
        {
            get
            {                
                return _name;
            }
            //set { _name = value; }
        }

    }

}