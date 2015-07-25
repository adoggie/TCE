
#ifndef _TCE_SOCKET_ADAPTER_H
#define _TCE_SOCKET_ADAPTER_H

#include "../adapter.h"

#include "../connection.h"
#include "../utils.h"

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>

namespace tce{
class RpcCommunicator;
class QSocketConnection;
class QSocketAdapter;
typedef boost::shared_ptr<QSocketAdapter> QSocketAdapterPtr;

class QSocketAdapter:public RpcCommAdapter { //,public boost::enable_shared_from_this<QSocketAdapter>{
public:
	~QSocketAdapter();
	friend class RpcCommunicator;
	QSocketAdapter();
	bool open(const std::string& uri,const options_type& opts = options_type() );
	void close();
	int onConnected(const RpcConnectionPtr& conn);
	void onDisconnected(const RpcConnectionPtr& conn); // Adapter作为应答服务时起效，比如 socket server
//	boost::asio::ip::tcp::socket& socket(){
//		return _sock;
//	}



private:
	void start();
	void stop();
	void handle_accept(const boost::system::error_code& ec, const boost::shared_ptr<RpcConnection>& conn);
private:
	//boost::asio::ip::tcp::socket _sock;
	//boost::asio::io_service * _ioservice;
	boost::asio::ip::tcp::acceptor _acceptor;
	//boost::mutex _mtxconns;
//	std::list< RpcConnectionPtr > _conns;
};


}

#endif

