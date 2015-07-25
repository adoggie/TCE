#ifndef _TCE_SOCKET_CONN_H
#define _TCE_SOCKET_CONN_H

#include "../connection.h"
#include "../utils.h"
#include "../bytearray.h"

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>

#include <deque>
#include <vector>
#include <list>
#include <string>

using namespace boost::asio::ip;

/**
 *
 *
 */

namespace tce{

class QSocketAdapter;

class QSocketConnection:public RpcConnection { //,public boost::enable_shared_from_this<QSocketConnection>{
	friend class QSocketAdapter;
public:
	~QSocketConnection();
	//QSocketConnection(QSocketAdapter* adapter);
	QSocketConnection();
	QSocketConnection(const std::string& uri,const Properties_t& opts = Properties_t());
	bool connect();
	void close();
	void destroy();
	bool sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec);
	boost::asio::ip::tcp::socket& socket(){
		return _sock;
	}
	bool isConnected();
public:
	void start();
	void stop();

private:
	bool doRead();
	bool doWrite();
	void handle_write( DataChunkPtr dc,boost::system::error_code ec,size_t bytes_transferred);
	void handle_read(DataChunkPtr dc,const boost::system::error_code& e,std::size_t bytes_transferred);
	void handle_connect(const boost::system::error_code& e);

	void reset();

	void onConnected();
	void onDisconnected();

	typedef ByteArray DataBuffer;
	typedef std::vector<boost::shared_ptr<DataBuffer> > DataBuffers;

	int parseData(const char *  d,size_t& size,DataBuffers& dbfs); // 1 - ok , 0 - need more, -1: data dirty
private:
	boost::asio::ip::tcp::socket _sock;
	//boost::asio::io_service & _ioservice;
//	boost::asio::ip::tcp::acceptor _acceptor;
	std::vector<char> _readbuf;
	//std::deque<char> _writebuf;
	std::vector<char> _tempread;
	//std::vector<char> _tempwrite;
	boost::mutex		_mtxread;
	boost::mutex 		_mtxwrite;

	DataChunkList _writebufs;

	DataChunkList _writebufsxx;
	//char 		_connstatus; // 1 - online , 0 - offline
//	QSocketAdapter* 	_adapter;

};

}
#endif
