
#include "tce2.h"
#include <tce/tce.h>

#include <string>
#include <vector>

class MyServer:public tce2::NetMgrServer{

	tce2::id_t getId(tce::RpcContext& ctx){
		tce2::id_t id;
		id.id = 101;
		id.name = "scott.bin";

		return id;
	}

	int shutdown(tce::RpcContext& ctx){
		return 0;
	}

	std::vector< tce2::DevRouter > enumRouterList(const std::string& filter,tce::RpcContext& ctx){
		return std::vector< tce2::DevRouter >();
	}

	tce2::ClientInfo getInfo(tce::RpcContext& ctx){
			return tce2::ClientInfo();
	}
};




void test_tce2(){
	tce::RpcCommunicator::instance().init();
	tce::RpcCommAdapterPtr adapter;
	adapter = tce::RpcCommunicator::instance().createAdatper(tce::RpcConnection::SOCKET,"127.0.0.1 12002");
	boost::shared_ptr<MyServer> server(new MyServer);
	adapter->addServant("myserver",server);
	tce::LOGTRACE("server started!");
	tce::RpcCommunicator::instance().exec();

}
