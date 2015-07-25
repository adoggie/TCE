
#ifndef _TCE_COMMUNICATOR_H
#define _TCE_COMMUNICATOR_H



/***
 * 1.添加队列处理线程,Qpid接收消息置入Communicator的任务队列
 *
 *
 *
 *
 */
#include "base.h"

#include <boost/shared_ptr.hpp>
#include "utils/atomseq.h"
#include "connection.h"
#include "adapter.h"
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/barrier.hpp>

#include <boost/asio.hpp>
#include <boost/asio/error.hpp>

#include "observer.h"

#include "utils/logger.h"
//#include "utils/log4cxx.h"

//#include <log4cpp/Category.hh>
//#include <log4cpp/PropertyConfigurator.hh>
#include "utils/plainconfig.h"

namespace tce{

/**
 * @brief RpcCommunicator 通信器，通过instance()访问，仅能存在一个
 *
 */
class RpcCommunicator{
	RpcCommunicator();
public:
	friend class RpcConnection;

	struct LocalProperties_t{
		size_t threadnum; //线程数量
		//std::string confile;
		std::string logfile;
		std::string svcname;
		bool msgDispOnConn; // msg recved on conn would not be dispatch to Communicator
		LocalProperties_t(){
			threadnum = 1;
			//confile = "/etc/tce.conf";
			logfile = "";
			msgDispOnConn = false;
		}
	};

	LocalProperties_t& getProps() {	return _props; }

	static RpcCommunicator& instance(){
		static boost::shared_ptr<RpcCommunicator> comm;
		if( !comm.get()){
			comm =boost::shared_ptr<RpcCommunicator>(new RpcCommunicator);
		}
		return *comm;
	}

	unsigned int getUniqueSequence();
	unsigned int currentTimeStamp();

	void enqueueMsg(boost::shared_ptr<RpcMessage>& m); //推入消息到队列

	bool init(const Properties_t& props = Properties_t())  ;

	void exec();
	void shutdown();

	RpcConnectionPtr createConnection( RpcConnection::Types type,const std::string& uri,const Properties_t& opts = Properties_t() );
	//RpcCommAdapterPtr createAdatper(RpcCommAdapter::Types type,const std::string& uri="",const Properties_t& opts = Properties_t() );
	RpcCommAdapterPtr createAdatper(const std::string& uri="",const Properties_t& opts = Properties_t() );
	RpcCommAdapterPtr getAdapter(const std::string& uri);

	void logTrace(const std::string& msg);
	TraceContext& getTraceContext();
	boost::asio::io_service& ioservice();
	void setLogger( const LoggerPtr& log);
	LoggerPtr& getLogger(){ return _logger;}

	void appendObserver(const MessageObserverPtr& observer); ///< 必须在运行之前完成添加观察员，内部访问观察员对象时不进行互斥处理
	uint16_t& localServiceId(){ return _localsvc_id;}
private:
	void thread_domsg();
	void thread_ioservice();
	void salfCheck();

	// o - do nothing; ;1 - proccessed
	int onMessagePut(RpcMessagePtr& m);
	int onMessageGet(RpcMessagePtr& m) ;// 消息提炼
//	log4cpp::Category* getLogger(const std::string& name="tce") const;
private:
	utils::AtomSequenceInt _seq;
	TraceContext	_tracectx;
	LocalProperties_t	_props;
	boost::thread_group  _threads;
	boost::mutex	_mtx;
	boost::mutex	_mtxmsg;
	boost::condition_variable	_condmsg;
	std::list< boost::shared_ptr<RpcMessage>  > _msglist;
	std::list< RpcConnectionPtr > _conns;

	boost::mutex _mtxadapters;
	std::map< std::string, RpcCommAdapterPtr > _adapters;
	bool	_exiting;
	boost::shared_ptr< boost::thread> _thread_ios;

	uint16_t _localsvc_id;	//本地服务编号，发送rpc随calltype一起到达远端，并随sequence返回
public:
	boost::asio::io_service& io_service(){ return _ios;}
	boost::asio::io_service  _ios;
	boost::shared_ptr<boost::asio::deadline_timer> _chktimer;
	boost::mutex _mtxlog;
	PlainConfig _conf;
	LoggerPtr _logger;
	std::vector< MessageObserverPtr > _observers; ///<允许添加多个消息观察者
public:
	void pushWaitMsg(RpcMessagePtr& m);
	RpcMessagePtr shiftWaitMsg(uint32_t sequence);
private:
	void onConnectionDisconnected(const RpcConnectionPtr& conn );

	boost::shared_mutex _mtxmsg_q;
	std::map<uint32_t,boost::shared_ptr<RpcMessage> > _msglist_q;

};

//#define CONSUMED 1
//#define IGNORED 0
//#define DROPPED CONSUMED

#define TRACECONTEXT TraceContextHelper(&RpcCommunicator::instance().getTraceContext())
#define LOGTRACE(x) RpcCommunicator::instance().logTrace(x)
#define LOGTCE RpcCommunicator::instance().getLogger()
}
#endif
