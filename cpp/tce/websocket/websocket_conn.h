#ifndef _TCE_WEBSOCKET_CONN_H
#define _TCE_WEBSOCKET_CONN_H

#ifdef _WEBSOCKET

#include "../connection.h"
#include "../utils.h"
#include "../bytearray.h"

//#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>

#include <deque>
#include <vector>
#include <list>
#include <string>

#include <websocketpp.hpp>

namespace tce{

class WebSocketAdapter;

class WebSocketConnection:public RpcConnection { //,public boost::enable_shared_from_this<QSocketConnection>{
	friend class WebSocketAdapter;
public:
	~WebSocketConnection(){}
	WebSocketConnection();
	WebSocketConnection(websocketpp::server::connection_ptr conn){
		_conn = conn;
		_type = WEBSOCKET;
	}
	WebSocketConnection(const std::string& uri,const Properties_t& opts = Properties_t());
	bool connect();
	void close();
	void destroy();
	bool sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec);
	bool isConnected();
public:
	void onMessage(websocketpp::message::data_ptr msg);
	void onConnected();
	void onDisconnected();
private:
	//void handle_read(DataChunkPtr dc,const boost::system::error_code& e,std::size_t bytes_transferred);

	void reset();



	typedef ByteArray DataBuffer;
	typedef std::vector<boost::shared_ptr<DataBuffer> > DataBuffers;

	int parseData(const char *  d,size_t& size,DataBuffers& dbfs); // 1 - ok , 0 - need more, -1: data dirty
private:
	std::vector<char> _readbuf;
	std::vector<char> _tempread;
	boost::mutex		_mtxread;
	boost::mutex 		_mtxwrite;
	DataChunkList _writebufs;
	DataChunkList _writebufsxx;

	websocketpp::server::connection_ptr _conn;
};

typedef boost::shared_ptr<WebSocketConnection> WebSocketConnectionPtr;

}

#endif

#endif
