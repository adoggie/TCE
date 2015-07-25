
#include "connection.h"
#include "message.h"
#include "communicator.h"
#include "adapter.h"
#include "utils/mutexobj.h"


/**
 *
 * 1.ÈìæÊé•‰∏¢Â§±ÔºåÈúÄË¶ÅÊ∏ÖÈô§ÁºìÂ≠òÁöÑmessage
 * 2.ÈÄöÁü•Âà∞twowayÊñπÂºèÁ≠âÂæÖÁöÑÁî®Êà∑Á∫øÁ®ãÔºàÊäõÂá∫ÂºÇÂ∏∏Ôºâ
 *  1.连接断开清除所有等待消息队列，并产生异常通知到调用线程
 *  2.调用返回如果错误结果，产生异常通知到调用线程
 *
 */
namespace tce{

RpcConnection::RpcConnection(const std::string& uri,const Properties_t& opts ){
	_type = UNKNOWN;
	_options = opts;
	_uri = uri;
	_insp = NULL;
	_sync = true;
	_connected = false;
	_destroyed = false;
	_ep_idx = 0;
	_userid = 0;
}

void RpcConnection::setOptions(const Properties_t& opts){
	this->_options = opts;
}

bool RpcConnection::connect(){
//	_sync = sync;

	return  false;
}

void RpcConnection::attachAdapter(const boost::shared_ptr<RpcCommAdapter>& adapter ){
	_adapter = adapter;
}

void RpcConnection::detachAdapter(){
	_adapter = boost::shared_ptr<RpcCommAdapter>();
}

void RpcConnection::close(){
	return void();
}

void RpcConnection::destroy(){
	_destroyed = true;
	close();
}

bool RpcConnection::sendMessage( boost::shared_ptr<RpcMessage> m){
	boost:: unique_lock<boost::shared_mutex> lock(_mtxmsg);
	m->issuetime = RpcCommunicator::instance().currentTimeStamp();
	if(RpcCommunicator::instance().onMessagePut(m) != MSG_IGNORED){ //observer已经处理，无需继续发送
		return true;
	}
	if( m->calltype & (RpcMessage::TWOWAY| RpcMessage::ASYNC) ){
		//m->lock =boost::shared_ptr<RpcMessage::AsyncLock>(new RpcMessage::AsyncLock);
		m->wait = boost::shared_ptr<MutexObject<RpcMessage> >( new MutexObject<RpcMessage>());
		//_msglist[m->sequence] = m;
		RpcCommunicator::instance().pushWaitMsg(m);
	}

	RpcConsts::ErrorCode ec;
	bool r;
	r = sendDetail(m,ec);

	if(!r){
//		std::map<uint32_t,boost::shared_ptr<RpcMessage> >::iterator itr;
//		itr = _msglist.find(m->sequence);
//		_msglist.erase(itr);
		if( m->calltype & (RpcMessage::TWOWAY| RpcMessage::ASYNC) ){
			RpcCommunicator::instance().shiftWaitMsg(m->sequence);
		}
	}
	//不再传递具体的错误码
	return r;
}

bool RpcConnection::routeMessage(boost::shared_ptr<RpcMessage>& m){
	boost:: unique_lock<boost::shared_mutex> lock(_mtxmsg);
	RpcConsts::ErrorCode ec;
	bool r;
	r = sendDetail(m,ec);
	return r;
}

bool RpcConnection::sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec){
	ec = RpcConsts::RPCERROR_SUCC;
	return false;
}

void RpcConnection::doReturnMsg(boost::shared_ptr<RpcMessage>& m2){

	std::map<uint32_t,boost::shared_ptr<RpcMessage> >::iterator itr;
	boost::shared_ptr<RpcMessage> m1;
	{
		/*
		boost::unique_lock<boost::shared_mutex> lock(_mtxmsg);
		itr = _msglist.find(m2->sequence);
		if(  itr != _msglist.end()){
			m1 = itr->second;
			_msglist.erase(itr);
		}else{
			//LOGTRACE("not  matched waiting user..");
			return; //Êú®ÊúâÁ≠âÂæÖÂØπË±°‰∫Ü
		}*/
		m1 = RpcCommunicator::instance().shiftWaitMsg(m2->sequence);
		if(m1.get() == NULL){
			return ;
		}
	}
	//找到匹配的等待消息
	//boost::shared_ptr<RpcMessage>& m1 = itr->second;
	//远端处理错误
	if(m2->errcode !=  RpcConsts::RPCERROR_SUCC){
		m1->exception = boost::shared_ptr<RpcException>(new RpcException( (RpcConsts::ErrorCode)m2->errcode));
	}
	if(m1->callback){ //async call
	 	(*(m1->callback) )(m1.get(),m2.get());
	 	return;
	}
	if(m1->wait.get()){
		MutexObject<RpcMessage>& mtx = *m1->wait;
		mtx.notify(m2); //
	}
	//ÂêåÊ≠•ÈÄöÁü•
}

bool RpcConnection::decodeMsg(ByteArray& d){

	boost::shared_ptr<RpcMessage> m;
	m = RpcMessage::unmarshall(d);
	return dispatchMsg(m);
}

bool RpcConnection::dispatchMsg( boost::shared_ptr<RpcMessage>& m){
	if(!m.get()){
		return false;
	}
	m->user_id = this->userId(); // 2012.11.25 scott
	m->conn = shared_from_this();
	if( m->calltype & RpcMessage::CALL){
		if(!_adapter.get()){
			return false;
		}

		_adapter->dispatchMsg(m,shared_from_this());
	}else{
		this->doReturnMsg(m);
	}
	return true;
}

void RpcConnection::execGC(){

}


void RpcConnection::onConnected(){
	this->_connected = true;
	//return ;
//	if(_insp)
//		_insp->onConnected(shared_from_this()  );
	LOGTRACE("onConnected()");
	if(_connevent_listen.get()){
		_connevent_listen->onConnected(shared_from_this());
	}
}

void RpcConnection::onDisconnected(){
	this->_connected = false;

//	if(_insp)
//		_insp->onDisconnected( shared_from_this() );

	if( _connevent_listen.get()) _connevent_listen->onDisconnected(shared_from_this());

	//清除消息等待队列,抛出异常
	{
		boost::unique_lock<boost::shared_mutex> lock(_mtxmsg);
		std::map<uint32_t,boost::shared_ptr<RpcMessage> >::iterator itr;
		for(itr=_msglist.begin(); itr!=_msglist.end();itr++){
			RpcMessage* m = (RpcMessage*)itr->second.get();
			m->exception = boost::shared_ptr<RpcException>(new RpcException(RpcConsts::RPCERROR_CONNECTION_LOST));
			if(m->wait.get()){
				m->wait->notify( boost::shared_ptr<RpcMessage>() );
			}
		}
		_msglist.clear();
	}
	LOGTRACE("onDisconnected()");
}

void RpcConnection::onFault(RpcConsts::ErrorCode code){
	_connected = false;
	if(_insp) _insp->onFalut(shared_from_this() );

	LOGTRACE("onFault()");

}


void RpcConnection::setInspector(InspectorPtr&  insp){
	_insp = insp;
}

void RpcConnection::handle_connect(const boost::system::error_code& ec){
	int a;
	a = 100;
	LOGTRACE("RpcConnection::handle_connect()");
}

void RpcConnection::handle_write( DataChunkPtr dc,boost::system::error_code ec,size_t bytes_transferred){
	LOGTRACE("RpcConnection::handle_write()");
}

void RpcConnection::handle_read(DataChunkPtr dc,const boost::system::error_code& ec,std::size_t bytes){
	LOGTRACE("RpcConnection::handle_read()");
}

void RpcConnection::setUserId(uint64_t userid){
	_userid = userid;
	if(_adapter.get()){
		_adapter->setUserId(shared_from_this());
	}
}




}
