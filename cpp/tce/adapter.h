
#ifndef _TCE_RPC_ADAPTER_H
#define _TCE_RPC_ADAPTER_H

#include "base.h"


#include "connection.h"
#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/utility.hpp>
#include <boost/enable_shared_from_this.hpp>
//#include "utils/atomseq.h"
#include <string>
#include <vector>
#include <map>
#include <algorithm>


//#include <websocketpp.hpp>

namespace tce{

struct RpcConsts;
class RpcServant;
class RpcMessage;
class RpcConnection;
class RpcCommunicator;
typedef boost::shared_ptr<RpcConnection> RpcConnectonPtr;

class RpcCommAdapter:public boost::enable_shared_from_this<RpcCommAdapter>{
public:
	RpcCommAdapter(){
		_ep_idx = 0 ;
	}
	virtual ~RpcCommAdapter(){}
public:
	typedef RpcConnection::Types Types;
	typedef std::map<std::string,std::string> options_type;

	friend class RpcCommunicator;
	void addServant(const std::string& name,const boost::shared_ptr<RpcServant>& servant );
	void removeServant(const std::string& name);
	virtual bool open(const std::string& uri,const options_type& opts = options_type() );
	virtual void close();
	uint16_t& ep_idx(){ return _ep_idx;}
protected:
	virtual int onConnected(const RpcConnectionPtr& conn);
	virtual void onDisconnected(const RpcConnectionPtr& conn); // Adapter作为应答服务时起效，比如 socket server

	virtual void doError(RpcConsts::ErrorCode code,boost::shared_ptr<RpcMessage>& m,boost::shared_ptr<RpcConnection>& conn);
	virtual void dispatchMsg(boost::shared_ptr<RpcMessage>& m,const boost::shared_ptr<RpcConnection>& conn);
	//virtual void dispatchMsg(boost::shared_ptr<RpcMessage>& m,RpcConnection* conn);
	friend class RpcConnection;
public:
	virtual void addConnection(const RpcConnectionPtr & conn);
	virtual void removeConnection(const RpcConnectionPtr& conn);
	void setUserId(const RpcConnectionPtr&conn);
	RpcConnectionPtr getConnectionByUserId(uint64_t userid);
public:
	virtual void handle_accept(const boost::system::error_code& ec,const boost::shared_ptr<RpcConnection>& conn){}

	void setConnectionEventListener(ConnectionEventListenerPtr listener);
	ConnectionEventListenerPtr connectionEventListener(){
		return _connevent_listen;
	}
protected:
	boost::mutex		_mtxservants;
	std::map< uint16_t, boost::shared_ptr<RpcServant> > _servants;
	std::string _uri;
	options_type _opts;

//	boost::mutex 	_mtxconns;
	boost::shared_mutex _mtxconns;
	std::list< boost::shared_ptr<RpcConnection>  > _conns;
	std::map<uint64_t,boost::shared_ptr<RpcConnection> > _id_conns; //
	uint16_t  _ep_idx;
	ConnectionEventListenerPtr _connevent_listen;
};

typedef boost::shared_ptr<RpcCommAdapter> RpcCommAdapterPtr;

}

#endif

