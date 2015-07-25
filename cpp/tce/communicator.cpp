
#include "communicator.h"

#include "qpid/qpid_adapter.h"
#include "qpid/qpid_conn.h"
#include "socket/sock_adapter.h"
#include "socket/sock_conn.h"
#include<boost/typeof/typeof.hpp>
#include <iostream>
#include <boost/format.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <string>


#include "qpid/mq_set.h"

namespace tce{

RpcCommunicator::RpcCommunicator(){
	_exiting = false;
	_localsvc_id = 0;
	_logger = LoggerPtr(new Logger());
}

unsigned int RpcCommunicator::getUniqueSequence(){
		/*
		boost::posix_time::ptime pt;
		boost::posix_time::from_time_t()
		boost::posix_time::second_clock::local_time()
		 	*/
	return _seq.nextval();
}


unsigned int RpcCommunicator::currentTimeStamp(){
	std::time_t t;

	std::time(&t);
	return (unsigned int) t;
}

void RpcCommunicator::enqueueMsg(boost::shared_ptr<RpcMessage>& m){

	if(!_props.msgDispOnConn){
		{
			boost::mutex::scoped_lock lock(_mtxmsg);
			_msglist.push_back(m);
		}
		_condmsg.notify_one();
	}else{
		if( onMessageGet(m) != MSG_IGNORED){
			return ; // drop it
		}
		m->conn->dispatchMsg(m);
	}
}


void RpcCommunicator::thread_domsg(){
	try{
		while(!_exiting){
			boost::shared_ptr<RpcMessage> m;
			{
				boost::mutex::scoped_lock lock(_mtxmsg);
				if(!_msglist.empty()){
					m = * _msglist.begin();
					_msglist.pop_front();
				}else{
					/*
					_condmsg.timed_wait(lock,boost::get_system_time() + boost::posix_time::milliseconds(20));
					if(!_msglist.empty()){
						m = * _msglist.begin();
						_msglist.pop_front();
					}*/
					while( _msglist.empty()){
							this->_condmsg.wait(lock);
					}
					m = *_msglist.begin();
					_msglist.pop_front();
				}
				//while( _msglist.empty()){
				//	this->_condmsg.wait(lock);
				//}
				// m = *_msglist.begin();
				//_msglist.pop_front();
			}
			if(m.get()){
				{
					if( onMessageGet(m) != MSG_IGNORED){
						continue; //消息丢弃
					}
				}
				m->conn->dispatchMsg(m);
			}

		}
	//}catch( boost::thread_interrupted& e ){
	}catch(std::exception& e){
		std::cout<<e.what()<<std::endl;
	}
	_exiting = true;
}

//注意，这里不加锁，如果必要可以使用共享读写锁
int RpcCommunicator::onMessageGet(RpcMessagePtr& m){
	std::vector< MessageObserverPtr >::iterator itr;
	for(itr = _observers.begin();itr!=_observers.end();itr++){
		int result = (*itr)->onMessageGet(m);
		if(  result!= MSG_IGNORED){
			return result; //已经被截取，无需继续分派
		}
	}
	return MSG_IGNORED ; //继续派发到本地Rpc接口
}

int RpcCommunicator::onMessagePut(RpcMessagePtr& m){
	std::vector< MessageObserverPtr >::iterator itr;
	for(itr = _observers.begin();itr!=_observers.end();itr++){
		int result = (*itr)->onMessagePut(m);
		if(  result!= MSG_IGNORED){
			return result; //已经被截取，无需继续分派
		}
	}
	return MSG_IGNORED ; //继续派发到本地Rpc接口
}


void RpcCommunicator::salfCheck(){
	//LOGTRACE("salfCheck()...");
	_chktimer->expires_from_now(boost::posix_time::seconds(5));
	_chktimer->async_wait( boost::bind(&RpcCommunicator::salfCheck,this));
}

bool RpcCommunicator::init( const Properties_t& props)  {
	// init logger
	std::string file,name;
	Properties_t::const_iterator itr;
	itr = props.find("svcfile");
	if(  itr == props.end()){
		return false;
	}
	file = itr->second;

	itr = props.find("svcname");
	if(  itr == props.end()){
		return false;
	}
	name = itr->second;
	this->_props.svcname = name;
	//s = props["svcfile"];
	if( !mqset_inst()->init(name,file)){
		return false;
	}
	return true;
}

extern void websocket_listen();

void RpcCommunicator::exec(){
	for(size_t n=0;n<_props.threadnum;n++){_threads.create_thread( boost::bind(&RpcCommunicator::thread_domsg,this));}
	_chktimer = boost::shared_ptr<boost::asio::deadline_timer>(new boost::asio::deadline_timer(_ios,boost::posix_time::seconds(5))) ;
	_chktimer->async_wait( boost::bind(&RpcCommunicator::salfCheck,this));
	_thread_ios = boost::shared_ptr<boost::thread>(new boost::thread(boost::bind(&boost::asio::io_service::run,&_ios )));
	log_info(LOGTCE,"Server < %s > Running...",%_props.svcname);
	//	_ios.run();
#ifdef _WEBSOCKET
	websocket_listen();
#endif
	_threads.join_all();
	_thread_ios->join();
}

void RpcCommunicator::shutdown(){
	{
		boost::mutex::scoped_lock lock( _mtxadapters);
		RpcCommAdapterPtr adapter;
		std::map< std::string, RpcCommAdapterPtr >::iterator itr;
		for(itr = _adapters.begin();itr!=_adapters.end();itr++){
			itr->second->close();
		}
		_adapters.clear();
	}

	_threads.interrupt_all();
	_ios.stop();
	_thread_ios->interrupt();
}

RpcConnectionPtr
RpcCommunicator::createConnection( RpcConnection::Types type,
		const std::string& uri,const Properties_t& opts ){
	if( type == RpcConnection::QPID){
#ifdef _QPID
		//return RpcConnectionPtr(new QpidConnection(uri,opts));
		RpcRouteEndPointPtr ep;
		ep = mqset_inst()->localserver()->findOutEnpoint(uri);
		if(ep.get() == NULL){
			return RpcConnectionPtr();
		}
		MQ_impl* mqptr = (MQ_impl*)ep->impl.get();
		return mqptr->conn;

#endif
	}else if( type == RpcConnection::SOCKET){
		return RpcConnectionPtr(new QSocketConnection(uri,opts) );
	}
	return RpcConnectionPtr();
}

RpcCommAdapterPtr
RpcCommunicator::createAdatper(
		const std::string& uri,const Properties_t& opts ){
//	if( type == RpcConnection::)
	RpcCommAdapterPtr adapter;


	RpcRouteEndPointPtr ep = mqset_inst()->localserver()->findOutEnpoint(uri);
	if( ep.get()){
		if( ep->type == RpcConnection::SOCKET){
			SocketAdapter_impl* asi = (SocketAdapter_impl*) ep->impl.get();
			adapter = asi->adapter;
		}else if( ep->type == RpcConnection::WEBSOCKET){
#ifdef _WEBSOCKET
			WebSocketAdapter_impl* asi = (WebSocketAdapter_impl*) ep->impl.get();
			adapter = asi->adapter;
#endif
		}else if( ep->type == RpcConnection::QPID){
#ifdef _QPID
			MQ_impl* mq = (MQ_impl*)ep->impl.get();
			adapter = RpcCommAdapterPtr(new QpidAdapter);
			mq->conn->attachAdapter(adapter); //绑定adaper到接受连接线程
#endif
		}
	}

// socket adapter已经在mqset启动时准备好了

//	if( type == RpcConnection::SOCKET){
//		adapter = QSocketAdapterPtr(new QSocketAdapter);
//		if( !adapter->open(uri,opts)){
//			adapter = RpcCommAdapterPtr();
//		}
//	}

	if(adapter.get()){
		//boost::mutex::scoped_lock lock( _mtxadapters);
		//_adapters[uri] = adapter;

	}
	return adapter;
}


RpcCommAdapterPtr RpcCommunicator::getAdapter(const std::string& uri){
	boost::mutex::scoped_lock lock( _mtxadapters);
	RpcCommAdapterPtr adapter;
	std::map< std::string, RpcCommAdapterPtr >::iterator itr;
	itr = _adapters.find( uri);
	if( itr!= _adapters.end()){
		adapter = itr->second;
	}
	return adapter;
}

void RpcCommunicator::logTrace(const std::string& msg){
	boost::mutex::scoped_lock lock(_mtxlog);
	std::cout<< msg << std::endl;
}

TraceContext& RpcCommunicator::getTraceContext() {
	return _tracectx;
}


boost::asio::io_service& RpcCommunicator::ioservice(){
	return _ios;
}

void RpcCommunicator::thread_ioservice(){
	while(1){
		try{
			size_t n = _ios.run();
			 boost::format fmt("ios.run() = %d");
			 fmt%n;
			LOGTRACE(fmt.str());
			_ios.reset();
			boost::this_thread::sleep( boost::posix_time::microseconds(20) );
			//boost::thread::sleep( boost::posix_time::seconds(1));
		}catch( std::exception& e){
			LOGTRACE(e.what());
			break;
		}
	}
	LOGTRACE("io_service exiting..");
}

void RpcCommunicator::setLogger( const LoggerPtr& log){
	_logger = log;
}

void RpcCommunicator::appendObserver(const MessageObserverPtr& observer){
	_observers.push_back(observer);
}


void RpcCommunicator::pushWaitMsg(RpcMessagePtr& m){
	boost:: unique_lock<boost::shared_mutex> lock(_mtxmsg_q);
	_msglist_q[m->sequence] = m;
}

RpcMessagePtr RpcCommunicator::shiftWaitMsg(uint32_t sequence){
	boost::unique_lock<boost::shared_mutex> lock(_mtxmsg_q);
	std::map<uint32_t,boost::shared_ptr<RpcMessage> >::iterator itr;
	itr = _msglist_q.find(sequence);
	RpcMessagePtr m;
	if(  itr != _msglist_q.end()){
		m = itr->second;
		_msglist_q.erase(itr);
	}
	return m;
}

void RpcCommunicator::onConnectionDisconnected(const RpcConnectionPtr& conn ){
	//增加定时器检查 消息是否超时，则删除，防止缓存溢出
}


}
