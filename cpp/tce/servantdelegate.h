
#ifndef _TCE_RPC_SERVANTDELEGATE_H
#define _TCE_RPC_SERVANTDELEGATE_H



#include "base.h"

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/smart_ptr.hpp>
#include <string>
#include <vector>
#include <map>
#include <algorithm>


namespace tce{

class RpcCommAdapter;
class RpcConnection;

class RpcContext;

typedef bool (* OperatorDummy_t)(RpcContext&);

class RpcServantDelegate{
public:
	RpcServantDelegate(){
		_index = 0;
	}
	~RpcServantDelegate(){}

	uint8_t ifidx(){ return _index;}

	void setAdapter(boost::shared_ptr<RpcCommAdapter>& adapter){
		_adapter = adapter;
	}
	//void setConnection(boost::shared_ptr<RpcConnection>* conn);
	std::map< uint16_t, OperatorDummy_t>& optlist(){
		return _optlist;
	}
	//bool opt_existed(uint16_t idx);
	OperatorDummy_t operation(uint16_t idx){
		std::map< uint16_t, OperatorDummy_t>::iterator itr;
		itr = _optlist.find(idx);
		if( _optlist.end() == itr){
			return NULL;
		}
		return itr->second;
	}
protected:
	uint8_t _index;
	boost::shared_ptr<RpcCommAdapter> _adapter;
	std::map< uint16_t, OperatorDummy_t> _optlist;
};

}

#endif

