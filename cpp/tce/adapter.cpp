
#include "adapter.h"


#include "message.h"
#include "connection.h"
#include "servant.h"
#include "context.h"
#include "exception.h"
#include "communicator.h"
#include "servantdelegate.h"



namespace tce{

void RpcCommAdapter::addServant(const std::string& name,const boost::shared_ptr<RpcServant>& servant  ){
	boost::mutex::scoped_lock(_mtxservants);
	this->_servants[servant->delegate()->ifidx()] = servant;
	servant->setAdapter(shared_from_this());
}

void RpcCommAdapter::removeServant(const std::string& name){
	boost::mutex::scoped_lock(_mtxservants);
	std::map<uint16_t, boost::shared_ptr<RpcServant> >::iterator itr;

	for(itr = _servants.begin(); itr!= _servants.end();itr++){
		if( itr->second->name() == name){
			_servants.erase(itr);
			break;
		}
	}
}

void RpcCommAdapter::doError(RpcConsts::ErrorCode code,
	boost::shared_ptr<RpcMessage>& m,
	boost::shared_ptr<RpcConnection>& conn){

}

void RpcCommAdapter::dispatchMsg(boost::shared_ptr<RpcMessage>& m,
	 const boost::shared_ptr<RpcConnection>& conn){
	//	 RpcConnection* conn){

	TRACECONTEXT<< "RpcCommAdapter::dispatchMsg";

	boost::mutex::scoped_lock(_mtxservants);
	std::map<uint16_t, boost::shared_ptr<RpcServant> >::iterator itr;
	if(m->calltype & RpcMessage::CALL){
		itr = _servants.find(m->ifidx);
		if(itr ==_servants.end()){
			//response with INTERFACE_NOT_FOUND
			RpcMessagePtr resp(new RpcMessageReturn);
			resp->sequence = m->sequence;
			resp->errcode = RpcConsts::RPCERROR_INTERFACE_NOTFOUND;
			resp->callmsg = m;
			conn->sendMessage(resp);
			return;
		}
		boost::shared_ptr<RpcServantDelegate>& dg = itr->second->delegate();

		OperatorDummy_t opt = dg->operation(m->opidx);
		if(!opt){
			//response with OPERATION_NOT_FOUND
			RpcMessagePtr resp(new RpcMessageReturn);
			resp->sequence = m->sequence;
			resp->errcode = RpcConsts::RPCERROR_INTERFACE_NOTFOUND;
			conn->sendMessage(resp);
			return;
		}
		RpcContext ctx;
		ctx.conn = conn;
		ctx.msg = m;
		ctx.delegate = dg.get();
		try{
			(*opt)(ctx);
			if(ctx.closeconn){
				conn->close(); //servant处理函数设置关闭连接
			}
		}catch( RpcException& e){
			// response with REMOTE_INVOKE_ERROR
			RpcMessagePtr resp(new RpcMessageReturn);
			resp->sequence = m->sequence;
			resp->errcode = RpcConsts::RPCERROR_REMOTE_EXCEPTION;
			conn->sendMessage(resp);
			LOGTRACE(e.what());
		}
	}
}


int RpcCommAdapter::onConnected(const RpcConnectionPtr& conn){
	return 1;
}

void RpcCommAdapter::onDisconnected(const RpcConnectionPtr& conn){

}

bool RpcCommAdapter::open(const std::string& uri,const options_type& opts ){
	_uri = uri;
	_opts = opts;
	return true;
}

void RpcCommAdapter::close(){

}

void RpcCommAdapter::addConnection(const RpcConnectionPtr & conn){
//	boost::mutex::scoped_lock lock(_mtxconns);
	boost::unique_lock<boost::shared_mutex> writelock(_mtxconns);
	_conns.push_back(conn);
	if( _connevent_listen.get()){
		conn->setConnectionEventListener(_connevent_listen);
	}
//	_id_conns[conn->userId()] = conn;
}

void RpcCommAdapter::setUserId(const RpcConnectionPtr&conn){
//	boost::mutex::scoped_lock lock(_mtxconns);
	boost::unique_lock<boost::shared_mutex> writelock(_mtxconns);

	_id_conns[conn->userId()] = conn;
}

void RpcCommAdapter::removeConnection(const RpcConnectionPtr& conn){
//	boost::mutex::scoped_lock lock(_mtxconns);
	boost::unique_lock<boost::shared_mutex> writelock(_mtxconns);

	std::list< RpcConnectionPtr >::iterator itr;
	//itr = _conns.find(conn);
	itr = std::find(_conns.begin(),_conns.end(),conn);
	if(itr != _conns.end()){
		_conns.erase(itr);
	}

	std::map<uint64_t,boost::shared_ptr<RpcConnection> >::iterator itr2;
	itr2 = _id_conns.find(conn->userId());
	if(itr2!=_id_conns.end()){
		_id_conns.erase(itr2);
	}

}


RpcConnectionPtr RpcCommAdapter::getConnectionByUserId(uint64_t userid){
	boost::shared_lock<boost::shared_mutex> readlock(_mtxconns);
	std::map<uint64_t,boost::shared_ptr<RpcConnection> >::iterator itr;
	itr = _id_conns.find(userid);
	if(itr != _id_conns.end()){
		return itr->second;
	}
	return RpcConnectionPtr();

}


void RpcCommAdapter::setConnectionEventListener(ConnectionEventListenerPtr listener){
	boost::unique_lock<boost::shared_mutex> readlock(_mtxconns);
	std::list< boost::shared_ptr<RpcConnection>  >::iterator itr;
	for(itr= _conns.begin();itr!=_conns.end();itr++){
		(*itr)->setConnectionEventListener(listener);
	}
	this->_connevent_listen = listener;
}



}

