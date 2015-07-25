
#ifndef _TCE_QPID_ADAPTER_H
#define _TCE_QPID_ADAPTER_H

#ifdef _QPID

#include "../adapter.h"
namespace tce{

class QpidAdapter:public RpcCommAdapter{

public:
	//friend  boost::shared_ptr<QpidAdapter>;
	~QpidAdapter(){}
	QpidAdapter(){}
	bool open(const std::string& uri,const options_type& opts = options_type() );
	void close();
	int onConnected(boost::shared_ptr<RpcConnection>& conn);
	void onDisconnected(boost::shared_ptr<RpcConnection>& conn); // Adapter作为应答服务时起效，比如 socket server


};


}

#endif

#endif

