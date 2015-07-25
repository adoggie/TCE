
#ifndef _TCE_RPC_PROXY_H
#define _TCE_RPC_PROXY_H


#include "connection.h"


#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>

#include <string>
#include <vector>
#include <map>
#include <algorithm>

namespace tce{

class RpcProxyBase;

class RpcMessage;

struct RpcAsyncCallBackBase{
	//boost::shared_ptr<RpcProxyBase> prx;
	virtual ~RpcAsyncCallBackBase(){};

};

class RpcProxyBase{

public:
	RpcProxyBase(){
		delta = NULL;
	}

	virtual ~RpcProxyBase(){}
	void * delta;
	boost::shared_ptr<tce::RpcConnection>  conn;
};

}

#endif

