
#ifndef _TCE_RPC_CONNECTION_H
#define _TCE_RPC_CONNECTION_H

#include "base.h"

//#include "adapter.h"
#include "message.h"

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/utility.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/system/error_code.hpp>

#include "utils/atomseq.h"
#include <string>
#include <vector>
#include <map>
#include <algorithm>

namespace tce{

class RpcCommAdapter;
class RpcCommunicator;
class RpcConnection;
typedef boost::shared_ptr<RpcConnection> RpcConnectionPtr;

struct ConnectionEventListener:boost::enable_shared_from_this<ConnectionEventListener>{
	virtual ~ConnectionEventListener(){}
	virtual void onConnected(const RpcConnectionPtr& conn){}
	virtual void onDisconnected(const RpcConnectionPtr& conn){}
	virtual void onFault(const RpcConnectionPtr& conn,RpcConsts::ErrorCode code){} //网络链接失败...
};
typedef boost::shared_ptr<ConnectionEventListener> ConnectionEventListenerPtr;

class RpcConnection:public boost::noncopyable,public boost::enable_shared_from_this<RpcConnection>{
public:
	//typedef std::map<std::string,std::string> options_type;
	typedef Properties_t options_type;
	enum Types{
		SOCKET,
		WEBSOCKET,
		QPID,
		USER,	// app call
		AUTO, 	// send back auto
		UNDEFINED,
		UNKNOWN =UNDEFINED,
		MQ = QPID
	};
private:
	//friend class RpcCommunicator;
public:
	RpcConnection(){}
	virtual ~RpcConnection(){};
	RpcConnection(const std::string &  uri,const Properties_t& opts = Properties_t());
	Types getType(){ return _type;}

	struct Inspector{
		virtual ~Inspector()=0;
		virtual void onConnected(const RpcConnectionPtr& conn);
		virtual void onDisconnected(const RpcConnectionPtr& conn);
		virtual void onFalut(const RpcConnectionPtr& conn);
	};
	//typedef boost::shared_ptr<Inspector> InspectorPtr;
	typedef Inspector* InspectorPtr;

	virtual void setOptions(const Properties_t& opts);
	//virtual bool connect(const std::string & uri);
	virtual bool connect();
	//virtual void attachAdapter(const std::string& name,boost::shared_ptr<RpcCommAdapter>& adapter );
	virtual void attachAdapter(const boost::shared_ptr<RpcCommAdapter>& adapter );
	//virtual void detachAdapter(const std::string& name);
	virtual void detachAdapter();
	virtual void close();
	virtual void destroy();
	bool syncConnect(){	return _sync;}
	virtual bool isConnected() { return _connected;}

	bool sendMessage( boost::shared_ptr<RpcMessage> m);
	void setInspector(InspectorPtr&  insp);

	uint64_t userId(){	return _userid;}
	void setUserId(uint64_t userid);

	uint16_t& ep_idx(){ return _ep_idx;}
	bool routeMessage(boost::shared_ptr<RpcMessage>& m);
	void closePrepare(); //标志connect不可用，在sendmessage之后关闭链接
	virtual bool sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec); //不同实现

	void setConnectionEventListener(ConnectionEventListenerPtr listener){
		_connevent_listen = listener;
	}
public:
 // dummy code
	virtual void handle_write( DataChunkPtr dc,boost::system::error_code ec,size_t bytes_transferred);
	virtual void handle_read(DataChunkPtr dc,const boost::system::error_code& ec,std::size_t bytes);
	virtual void handle_connect(const boost::system::error_code& ec);
protected:
	friend class RpcCommunicator;

	virtual void onConnected();
	virtual void onDisconnected();
	virtual void onFault(RpcConsts::ErrorCode code); //网络链接失败...


	virtual bool decodeMsg(ByteArray& d);
	virtual void doReturnMsg(boost::shared_ptr<RpcMessage>& m);
	virtual void execGC();	//垃圾回收

	virtual bool dispatchMsg( boost::shared_ptr<RpcMessage>& m);

	//typedef boost::shared_lock<boost::shared_mutex> readLock;
	//typedef boost:: unique_lock<boost::shared_mutex> writeLock;
protected:
	Properties_t _options;
	std::string _uri;
	Types	_type;
	boost::mutex _mtx;
	boost::shared_mutex _mtxadps;
	//std::map<std::string,boost::shared_ptr<RpcCommAdapter> > _adapters;
	boost::shared_ptr<RpcCommAdapter> _adapter;
	boost::shared_mutex _mtxmsg;
	std::map<uint32_t,boost::shared_ptr<RpcMessage> > _msglist;
	InspectorPtr  _insp;
	bool _sync; 	//conenct mode
	bool _connected;
	bool _destroyed;
	uint64_t 	_userid;

	uint16_t   _ep_idx;
	//RpcConnectionPtr _budyconn; //伙伴连接，socket指向自己

	ConnectionEventListenerPtr _connevent_listen;


};

//typedef boost::shared_ptr<RpcConnection> RpcConnectionPtr;


}

#endif

