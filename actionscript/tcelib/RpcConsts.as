
package tcelib{

	public class RpcConsts{
		public static const RPCERROR_SUCC:int = 0;
		public static const RPCERROR_SENDFAILED:int = 1;
		public static const RPCERROR_TIMEOUT:int  =2;
		public static const RPCERROR_DATADIRTY:int = 3;
		public static const RPCERROR_INTERFACE_NOTFOUND:int = 4; // #adapter中无法定位到接口函数
		public static const RPCERROR_UNSERIALIZE_FAILED:int = 5; // #解析rpc参数失败
		public static const RPCERROR_REMOTEMETHOD_EXCEPTION:int = 6; // #rpc 远端服务函数调用异常
		
		public static const MSGTYPE_RPC:int = 1;
	}


}