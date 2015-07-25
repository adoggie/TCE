

/*
 * 娘唉，qpid的queue和exchange机制导致无法实现发送和接收的匹配，之前没考虑清除
 * 调试时方才想起来
 * 务必去除接受队列，仅存发送队列，也就是qpid都是单向发送了
 * 调用模式也必须时 oneway方式了
 *
 *
 *
 */

#ifdef _QPID

#include "qpid_conn.h"
#include "../message.h"
#include "../communicator.h"

#include "mq_set.h"

#include <string>

namespace tce{

QpidConnection::~QpidConnection(){
	close();
	if( _thread.get() ){
		_thread->interrupt();
		_thread->join();
	}
}

QpidConnection::QpidConnection(){
	_type = QPID;
}

QpidConnection::QpidConnection(const RpcRouteEndPointPtr& ep){
	_type = QPID;
	_ep = ep;
}


bool QpidConnection::isConnected(){
	if( _conn.get() == NULL){
		return false;
	}
	return _conn->isOpen();
}

bool QpidConnection::connect(){
//	RpcConnection::connect(sync);
	try{
		if( this->isConnected() ){
			return true;
		}
		//std::string connectionOptions = "{sasl_mechanisms:GSSAPI, username:guest, password:guest }";
		boost::format fmt("%s:%d");
		fmt%_ep->host%_ep->port;

		_conn = boost::shared_ptr< messaging::Connection>(new messaging::Connection(fmt.str(), ""));
		_conn->setOption("tcp_nodelay",true);
		_conn->open();
		_session = _conn->createSession();
		_session.sync(false);

		if( _ep->access & AF_READ){
			log_debug(LOGTCE,"mq READ %s",%_ep->name);
			_recver = _session.createReceiver( _ep->address);
			_recver.setCapacity(4000);
			_thread = boost::shared_ptr<boost::thread>( new boost::thread( boost::bind(&QpidConnection::readThread,this) ) );
		}
		if( _ep->access & AF_WRITE){
			log_debug(LOGTCE,"mq WRITE %s",%_ep->name);
			_sender = _session.createSender(_ep->address);
		}
		log_debug(LOGTCE,"mq : <%s> open succ!",%_ep->name);
	}catch( std::exception& e){ //打开异常
		_conn->close();
		log_error(LOGTCE,"mq init failed! (mq broker %s:%d) detail:%s",%_ep->host%_ep->port%e.what());
//		this->onFault(RpcConsts::RPCERROR_CONNECT_UNREACHABLE);
		return false;
	}
	return true;
}

void QpidConnection::close(){
//	_recver.close();
	if(_conn->isOpen()){
		_conn->close();
	}
}

bool QpidConnection::sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec){
	QMssageAttribute_t attr;
	attr.src_type = Singleton<MqSet>::instance()->server()->service->id;
	attr.src_idx = Singleton<MqSet>::instance()->server()->id ;
	attr.user_id = m->user_id;	// 路由in连接上的userid

	boost::shared_ptr<ByteArray> bytes;
	try{
//		std::map<std::string,std::string> props = m->extra.getStrDict();
//		props["__sender_id__"] = boost::lexical_cast<std::string>(RpcCommunicator::instance().localServiceId());
//		m->extra.set(props);

		bytes = m->marshall();
		messaging::Message msg((char*)bytes->data(),bytes->size());
//		msg.setProperty("src_type", qpid::types::Variant(attr.src_type));
//		msg.setProperty("src_idx", qpid::types::Variant(attr.src_idx));
//		msg.setProperty("user_id", qpid::types::Variant(attr.user_id));
		_sender.send(msg);
	}catch(std::exception & e){
		log_error(LOGTCE,"Qpid sendMessage error! detail:%s",%e.what());
		return false;
	}
	return true;
}

/**
 *  线程进入接收消息，如果qpid服务下线，接收会抛出异常
 *
 */
void QpidConnection::readThread(){
	char * data;
	size_t size;
	this->onConnected();

	try{

		while(true){
			messaging::Message m = _recver.fetch(messaging::Duration::FOREVER );
			data = (char*) m.getContentPtr();
			size = m.getContentSize();
			ByteArray bytes(data,size);
			boost::shared_ptr<RpcMessage> msg = RpcMessage::unmarshall( bytes );
			if( msg.get() ){
//				QMssageAttributePtr attr(new QMssageAttribute_t);

				msg->conn = shared_from_this();
//				qpid::types::Variant::Map& props = m.getProperties();
//				msg->user_id = props["user_id"].asUint64();
//				attr->src_idx = props["src_idx"].asUint16();
//				attr->src_type = props["src_type"].asUint16();
//				attr->user_id = msg->user_id;
//				msg->delta = attr;
				try{
					std::string value = msg->extra.getValue("__user_id__","0");
					msg->user_id = boost::lexical_cast<uint64_t>(value);
				}catch(std::exception& e ){
					log_error(LOGTCE,"mq read one ,__user_id__ invalid!");
				}
				RpcCommunicator::instance().enqueueMsg(msg);
			}
			_session.acknowledge();
		}
	}catch(std::exception& e ){
		log_error(LOGTCE,"readThread exception! detail:%s",%e.what());
		log_info(LOGTCE,"qpid Thread exiting...");
	}
	_conn->close();
	this->onDisconnected();
}


}

#endif



