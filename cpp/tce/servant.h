
#ifndef _TCE_RPC_SERVANT_H
#define _TCE_RPC_SERVANT_H



#include "base.h"

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>

#include <string>
#include <vector>
#include <map>
#include <algorithm>

namespace tce{

class RpcProxyBase;
class RpcServantDelegate;
class RpcCommAdapter;

class RpcServant{
public:
	//RpcServant(const std::string& name);
	RpcServant(){}
	virtual ~RpcServant(){}
	std::string& name(){ return _name;};
	boost::shared_ptr<RpcServantDelegate>& delegate(){ return _delegate;}
	void setAdapter(const boost::shared_ptr<RpcCommAdapter>& adapter){
		_adapter = adapter;
	}

	boost::shared_ptr<RpcCommAdapter> getAdapter(){
		return _adapter;
	}
protected:
	std::string _name;
	boost::shared_ptr<RpcServantDelegate> _delegate;
	boost::shared_ptr<RpcCommAdapter> _adapter;
};

}

#endif

