
#ifndef _TCE_RPC_MESSAGE_H
#define _TCE_RPC_MESSAGE_H

#include "base.h"
//#include "servant.h"
//#include "proxy.h"
#include "bytearray.h"
#include "extra_data.h"


#include "utils/mutexobj.h"
//#include "communicator.h"

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/thread/condition_variable.hpp>

#include <string>
#include <vector>
#include <map>
#include <algorithm>

namespace tce{

#define  MSGTYPE_RPC 1

class RpcAsyncCallBackBase;
class RpcProxyBase;
class RpcConnection;



#define PACKET_STREAM_DATA


class RpcMessage{
public:
	enum CallType{
		CALL = 0x01,
		RETURN = 0x02,
		TWOWAY = 0x10,
		ONEWAY = 0x20,
		ASYNC = 0x40 	//异步调用
	};
	
	

	//void addParam(boost::shared_ptr<ByteArray>& p);
	boost::shared_ptr<ByteArray> marshall();
	static boost::shared_ptr<RpcMessage> unmarshall(ByteArray & d);

	RpcMessage(){
		type 		= MSGTYPE_RPC;
		calltype 	= CALL | TWOWAY;
		sequence 	= 0;
		ifidx 		= 0;
		opidx 		= 0;
		errcode 	= RpcConsts::RPCERROR_SUCC;
		timeout 	= 0;
		issuetime 	= 0;
		async 		= NULL;
		prx = NULL;
		paramsize = 0;
		callback = 0;
		callfrom = CF_LOCAL; ///<默认本地用户进程发起
		//delta = NULL；
		//delta = NULL;
		call_id = 0; ///<调用者的标识
		ep_idx  =0;
		user_id = 0;
	}

	PACKET_STREAM_DATA	int8_t type;	//消息类型 ，Rpc还是其他流消息
	PACKET_STREAM_DATA	int8_t calltype;
	PACKET_STREAM_DATA	uint32_t sequence;	//事务号
	PACKET_STREAM_DATA	uint16_t ifidx;	//接口编号
	PACKET_STREAM_DATA	uint16_t opidx;	//函数编号
	PACKET_STREAM_DATA	int32_t errcode;	//错误码
	PACKET_STREAM_DATA	int8_t 	paramsize;	//参数个数
	PACKET_STREAM_DATA	int16_t  call_id;	///<发送者类型，用于标识路由中的系统节点，call消息的此id，必须在return消息包将此id带回
	PACKET_STREAM_DATA	RpcExtraData extra; ///< >=4 bytes
	//以上属性打包
	enum CallFrom{
		CF_LOCAL=0,	///< 调用消息由本地应用产生，也是默认类型
		CF_CONNECTION = 1, ///< 调用消息从链路上到达的，在路由时采用
	};
	uint8_t  callfrom;
	ByteArray paramstream;
	uint16_t	ep_idx;	 //标识消息从那个endpoint上传送上来， 0-表示本地用户发起的user消息
	uint32_t timeout;	//超时限制
	uint32_t issuetime;	//发送时间

	RpcAsyncCallBackBase* async; //异步调用返回接口
	RpcProxyBase * prx;	// 调用代理
	//void * delta;	//上下文数据
	TceDeltaPtr	delta;
	uint64_t user_id;

	void (*callback)(RpcMessage*,RpcMessage*); //反射函数点

	boost::shared_ptr<RpcConnection> conn;

//	std::list< boost::shared_ptr<ByteArray> > params;
	boost::shared_ptr< RpcException >exception;

	struct AsyncLock{
		boost::mutex mtx;
		boost::condition_variable cond;
	};

	//boost::shared_ptr<AsyncLock> lock;
	boost::shared_ptr< MutexObject< RpcMessage> > wait;
	boost::shared_ptr<RpcMessage> callmsg;	//发送请求的msg
//	void addParam(  boost::shared_ptr<ByteArray>  bytes){
//		params.push_back(bytes);
//	}

};

typedef boost::shared_ptr<RpcMessage> RpcMessagePtr;

/***
 * call
 */
struct RpcMessageCall:public RpcMessage{
	RpcMessageCall(uint8_t flags = TWOWAY);
};

struct RpcMessageReturn:public RpcMessage{
	RpcMessageReturn(uint8_t flags = 0);

};



}

#endif

