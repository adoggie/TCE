
#include "ep.h"
#include "mq_set.h"
#include "../socket/sock_conn.h"
#include "../socket/sock_adapter.h"
#include "../utils.h"

#include "../websocket/websocket_conn.h"
#include "../websocket/websocket_adapter.h"



namespace tce{

#ifdef _QPID
bool MQ_impl::open( RpcRouteEndPointPtr& ep){
	if( conn.get()){
		return true; //已经链接
	}

	conn = QpidConnectionPtr( new QpidConnection(ep));
	conn->ep_idx() = ep->id;

	return conn->connect();
}

static uint64_t direct_rand_seq = 0;

bool MQ_impl::sendMessage(boost::shared_ptr<RpcMessage>& msg){
	//如果是socket进入的消息，找到user_id作为 extra传递到内部mq
	if(msg->conn->getType() == RpcConnection::SOCKET
			|| msg->conn->getType() == RpcConnection::WEBSOCKET){
		//如果连接未进行验证, conn->user_id == NULL, 不允许转发，直接挂断链接
		std::string value;
		value = utils::getPropertyValue(mqset_inst()->localserver()->props,std::string("userid_check"),std::string("true"));
		if(value == "true"){
			if( msg->conn->userId() == 0){
				msg->conn->close();
				return false;
			}
		}else{
			msg->conn->setUserId(direct_rand_seq++);
		}

//		if( msg->conn->userId() == 0){
//			msg->conn->close();
//			return false;
//		}

		std::map<std::string,std::string> props = msg->extra.getStrDict();
		props["__user_id__"] = boost::lexical_cast<std::string>(msg->conn->userId());
		msg->call_id = RpcCommunicator::instance().localServiceId();
		msg->call_id|=1<<15; //最高位置1表示路由消息包，返回时判别是否是本地gwa失败，则转发到终端设备
		msg->extra.set(props);
	}

	return conn->routeMessage(msg);
}

void MQ_impl::close(){

}

#endif

////////////////////////////////////////////////////////////////////////
///从msg中找出route in 带入的user_id,找到对应的连接，并通过连接发送出去
bool SocketAdapter_impl::sendMessage(boost::shared_ptr<RpcMessage>& msg){
	RpcConnectionPtr conn;
	conn = adapter->getConnectionByUserId(msg->user_id);
	if(!conn.get()){
		return false;
	}

	return conn->routeMessage(msg);
}

bool SocketAdapter_impl::open( RpcRouteEndPointPtr& ep_){
	boost::format fmt("%s:%d");
	fmt%ep_->host%ep_->port;
	log_debug(LOGTCE,"ep: %s %s %d",%ep_->name%ep_->host%ep_->port);

	if(adapter.get()){
		return true;
	}

	adapter = QSocketAdapterPtr(new QSocketAdapter);
	if( !adapter->open( fmt.str() )){
		return false;
	}
	adapter->ep_idx() = ep_->id;
	ep = ep_;
	return adapter.get() != NULL;
};

////// websocket ////////////////////////////////////////////////////////////////
#ifdef _WEBSOCKET
bool WebSocketAdapter_impl::sendMessage(boost::shared_ptr<RpcMessage>& msg){
	RpcConnectionPtr conn;
	conn = adapter->getConnectionByUserId(msg->user_id);
	if(!conn.get()){
		return false;
	}
	return conn->routeMessage(msg);
}

bool WebSocketAdapter_impl::open( RpcRouteEndPointPtr& ep_){
	boost::format fmt("%s:%d");
	fmt%ep_->host%ep_->port;
	log_debug(LOGTCE,"ep: %s %s %d",%ep_->name%ep_->host%ep_->port);

	if(adapter.get()){
		return true;
	}

	adapter = WebSocketAdapterPtr(new WebSocketAdapter);
	if( !adapter->open( fmt.str() )){
		return false;
	}
	adapter->ep_idx() = ep_->id;
	ep = ep_;
	return adapter.get() != NULL;
};

#endif

//////////////////////////////////////////////////////////////////////

bool AutoBack_impl::sendMessage(boost::shared_ptr<RpcMessage>& msg){
	if( msg->callmsg->conn->getType() == RpcConnection::QPID){
		if( msg->callmsg->delta.get() ){
//			QMssageAttributePtr attr = msg->callmsg->delta;
			RpcRouteEndPointPtr ep;
			uint8_t type,id;
			type = (msg->call_id>>8)&0xff;
			id = msg->call_id & 0xff;
			ep = mqset_inst()->getRouteEndpointWithMqAttr(type,id);
			if(ep.get()){
				return ep->impl->sendMessage(msg);
			}else{
				log_error(LOGTCE,"AutoBack_impl::sendMessage() mq-back cannt found!");
				return false;
			}
		}
	}else if ( msg->callmsg->conn->getType() == RpcConnection::SOCKET){
		RpcConsts::ErrorCode ec;
		return msg->callmsg->conn->sendDetail(msg,ec);
	}
	return false;
}

bool AutoBack_impl::open( RpcRouteEndPointPtr& ep){
	return true;
}

void AutoBack_impl::close(){

}


}
