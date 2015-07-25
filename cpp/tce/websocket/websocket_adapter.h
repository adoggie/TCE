
#ifndef _TCE_WEBSOCKET_ADAPTER_H
#define _TCE_WEBSOCKET_ADAPTER_H

#ifdef _WEBSOCKET

#include "../adapter.h"

#include "../connection.h"
#include "../utils.h"

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>

//#include "websocket_conn.h"

namespace tce{
class RpcCommunicator;

class WebSocketConnection;
typedef boost::shared_ptr<WebSocketConnection> WebSocketConnectionPtr;
class WebSocketAdapter;
typedef boost::shared_ptr<WebSocketAdapter> WebSocketAdapterPtr;

class WebSocketAdapter:public RpcCommAdapter {
public:
	~WebSocketAdapter();
	friend class RpcCommunicator;
	WebSocketAdapter();
	bool open(const std::string& uri,const options_type& opts = options_type() );
	void close();
	int onConnected(const RpcConnectionPtr& conn);
	void onDisconnected(const RpcConnectionPtr& conn); // Adapter作为应答服务时起效，比如 socket server

	class websocket_handler:public websocketpp::server::handler{
	public:
		websocket_handler( WebSocketAdapter* master){
			adapter = master;
		}
		void on_open(websocketpp::server::connection_ptr con);
		void on_close(websocketpp::server::connection_ptr con);

		void on_message(websocketpp::server::connection_ptr con,websocketpp::message::data_ptr msg);
		WebSocketAdapter * adapter;

	};
private:
	void on_open(websocketpp::server::connection_ptr con);
	void on_close(websocketpp::server::connection_ptr con);
	void on_message(websocketpp::server::connection_ptr con,websocketpp::message::data_ptr msg);
	void listenThread(const std::string& port);
	void salfCheck();
private:
	websocketpp::server::handler::ptr _handler;
	websocketpp::server::ptr _endpoint;

	boost::shared_mutex  _mtxconns;
	std::map<websocketpp::server::connection_ptr,WebSocketConnectionPtr> _connsmap;

	boost::shared_ptr<boost::thread> _thread;
	int _listen_port;
	boost::shared_ptr<boost::asio::deadline_timer> _chktimer;
};


}

#endif

#endif

