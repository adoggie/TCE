
#ifndef _TCE_RPC_CONTEXT_H
#define _TCE_RPC_CONTEXT_H


#include "connection.h"
#include "message.h"

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>

#include <string>
#include <vector>
#include <map>
#include <algorithm>

namespace tce{

class RpcServantDelegate;

struct RpcContext{
	boost::shared_ptr<RpcMessage> msg;
	boost::shared_ptr<RpcConnection> conn;
	RpcServantDelegate*  delegate;
	std::string nextmq;	//投递消息队列
	bool closeconn;

//	bool ignore_return;
	RpcContext(){
		delegate = NULL;
		closeconn = false;
//		ignore_return = false;
	}

//	void ignore(bool t){
//		ignore_return = t;
//	}
};

}

#endif
