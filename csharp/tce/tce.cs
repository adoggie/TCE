
using System;

namespace Tce {

    class RpcConstValue {
        public const int COMPRESS_ONE = 0;
        public const int COMPRESS_ZLIB = 1;
        public const int COMPRESS_BZIP2 = 2;
        
        public const int ENCRYPT_NONE = 0;
        public const int ENCRYPT_MD5 = 1;
        public const int ENCRYPT_DES = 2;

        public const int MSGTYPE_RPC = 1;
        public const int MSGTYPE_NORPC = 2;

        public const int CONNECTION_UNKNOWN = 0;
        public const int CONNNECTION_SOCK = 1;
        public const int CONNECTION_HTTP = 2;
        public const int CONNECTION_SSL = 0x10;

        public const int MSG_ENCODE_BIN = 0x10;
        public const int MSG_ENCODE_XML = 0x20;

        public const int ASYNC_RPCMSG = 0x01;

        public const string EXTRA_DATA_MQ_RETURN = "__mq_return__";
        public const string EXTRA_DATA_USER_ID = "__user_id__";
    }

   

}