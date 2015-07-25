#ifdef _QPID

#include "qpid_adapter.h"

namespace tce{


bool QpidAdapter::open(const std::string& uri,const options_type& opts  ){
	return RpcCommAdapter::open(uri,opts);
}

void QpidAdapter::close(){
	return RpcCommAdapter::close();
}

int QpidAdapter::onConnected(boost::shared_ptr<RpcConnection>& conn){
	return RpcCommAdapter::onConnected(conn);
}

void QpidAdapter::onDisconnected(boost::shared_ptr<RpcConnection>& conn){
	return RpcCommAdapter::onDisconnected(conn);
}


}


#endif
