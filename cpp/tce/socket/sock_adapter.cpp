
#include "sock_adapter.h"
#include "../communicator.h"
#include "sock_conn.h"
 #include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

namespace tce{


bool QSocketAdapter::open(const std::string& uri,const options_type& opts  ){
	RpcCommAdapter::open(uri,opts);
	_acceptor.open( boost::asio::ip::tcp::v4());
	std::vector<std::string> params;
	boost::split( params,uri,boost::is_any_of(": \t"),boost::token_compress_on);

	if(params.size()<2){
		return false;
	}
	try{
		boost::asio::ip::address addr =  boost::asio::ip::address::from_string( params[0]);
		uint16_t port;
		port = boost::lexical_cast<uint16_t>(params[1]);

		boost::asio::ip::tcp::endpoint ep(addr,port);

		_acceptor.set_option( boost::asio::socket_base::reuse_address(true));
		_acceptor.bind(ep);
		_acceptor.listen( boost::asio::socket_base::max_connections);

		start();
	}catch(std::exception& e){
		LOGTRACE(e.what());
		return false;
	}
	return true;
}

void QSocketAdapter::close(){
	return RpcCommAdapter::close();
}

int QSocketAdapter::onConnected(const RpcConnectionPtr& conn){
	return RpcCommAdapter::onConnected(conn);
}

void QSocketAdapter::onDisconnected(const  RpcConnectionPtr& conn){
	return RpcCommAdapter::onDisconnected(conn);
}


QSocketAdapter::QSocketAdapter():_acceptor(RpcCommunicator::instance().ioservice()){
//	_acceptor.get_io_service() = RpcCommunicator::instance().ioservice();

}

QSocketAdapter::~QSocketAdapter(){

}

void QSocketAdapter::handle_accept(const boost::system::error_code& ec, const
		boost::shared_ptr<RpcConnection>& conn){
	if(ec){
		return;
	}
	QSocketConnection *sc = (QSocketConnection*) conn.get();
	addConnection( conn );
	conn->ep_idx() = this->ep_idx(); //
	sc->attachAdapter(shared_from_this());
	sc->onConnected();
	sc->start();

	start();
}

void QSocketAdapter::start(){
	boost::shared_ptr<QSocketConnection> conn(new QSocketConnection);
	_acceptor.async_accept( conn->socket(),
			boost::bind(&RpcCommAdapter::handle_accept,shared_from_this(),boost::asio::placeholders::error,conn));

}

void QSocketAdapter::stop(){

}




}
