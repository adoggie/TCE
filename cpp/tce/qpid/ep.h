
#ifndef _TCE_ENDPOINT_H
#define _TCE_ENDPOINT_H

#include "../base.h"
//#include "qpid_conn.h"
#include "../adapter.h"
#include "../connection.h"

namespace tce{

struct IEndPointImpl;
typedef boost::shared_ptr<IEndPointImpl> IEndPointImplPtr;
struct RpcRouteEndPoint_t{
typedef  RpcConnection::Types Type;

	std::string name;
	std::string address;
	Type type;
	std::string host;
	int 	port;
	std::string user;
	std::string passwd;
	IEndPointImplPtr impl;
	uint16_t id;
	uint16_t  access; //AccessFlags
	RpcRouteEndPoint_t(){
		id = 0;
		access = 0;
		port = 0;
		type = RpcConnection::UNDEFINED;
	}
};
typedef boost::shared_ptr<RpcRouteEndPoint_t> RpcRouteEndPointPtr;


struct IEndPointImpl{

	virtual ~IEndPointImpl()=0;
	virtual bool sendMessage(boost::shared_ptr<RpcMessage>& msg)=0;
	virtual bool open( RpcRouteEndPointPtr& ep)=0;
	virtual void close(){};
};
inline
IEndPointImpl::~IEndPointImpl(){}

#ifdef _QPID
class QpidConnection;
typedef boost::shared_ptr<QpidConnection> QpidConnectionPtr;
struct MQ_impl:public IEndPointImpl{

	QpidConnectionPtr conn;
	bool sendMessage(boost::shared_ptr<RpcMessage>& msg);
	bool open( RpcRouteEndPointPtr& ep);
	void close();
};
typedef boost::shared_ptr<MQ_impl> MQ_implPtr;

#endif

struct SocketAdapter_impl:public IEndPointImpl{
	RpcCommAdapterPtr adapter;
	bool sendMessage(boost::shared_ptr<RpcMessage>& msg);
	bool open( RpcRouteEndPointPtr& ep);
	void close(){}
	RpcRouteEndPointPtr ep;
};
typedef boost::shared_ptr<SocketAdapter_impl> SocketAdapter_implPtr;

struct AutoBack_impl:public IEndPointImpl{
	bool sendMessage(boost::shared_ptr<RpcMessage>& msg);
	bool open( RpcRouteEndPointPtr& ep);
	void close();
};


struct UnRealize_impl:public IEndPointImpl{
	bool sendMessage(boost::shared_ptr<RpcMessage>& msg){
		return true;
	}
	bool open( RpcRouteEndPointPtr& ep){
		return true;
	}
	void close(){

	}
};

#ifdef _WEBSOCKET
struct WebSocketAdapter_impl:public IEndPointImpl{
	RpcCommAdapterPtr adapter;
	bool sendMessage(boost::shared_ptr<RpcMessage>& msg);
	bool open( RpcRouteEndPointPtr& ep);
	void close(){}
	RpcRouteEndPointPtr ep;
};
typedef boost::shared_ptr<SocketAdapter_impl> SocketAdapter_implPtr;
#endif

} // end tce namespace

#endif
