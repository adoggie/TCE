#ifndef _TCE_QPID_CONN_H
#define _TCE_QPID_CONN_H

#ifdef _QPID

#include "../connection.h"
#include "mq.h"


#include <boost/thread/thread.hpp>
#include <boost/thread/barrier.hpp>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>

#include <qpid/messaging/Connection.h>
#include <qpid/messaging/Message.h>
#include <qpid/messaging/Receiver.h>
#include <qpid/messaging/Sender.h>
#include <qpid/messaging/Session.h>
using namespace qpid ; //::messaging;

/**
 * qpid 不区分客户与服务器，两端通信必须建立各自的连接，并将本地的adapter绑定到各自的连接上
 * 或者打开adapter提供外部客户调用
 *
 */

namespace tce{

class QpidConnection:public RpcConnection{

public:
	~QpidConnection();
//	QpidConnection();
//	QpidConnection(const MQ_detail_t& detail ,AccessFlags af = AF_READ);
//	QpidConnection(const std::string& mq_write);
	QpidConnection(const RpcRouteEndPointPtr& ep);
	QpidConnection();

	bool connect();
	void close();
	bool sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec);
	bool isConnected();
private:
	void readThread();
private:
	boost::shared_ptr<messaging::Connection> _conn;
	messaging::Session  _session;
	messaging::Receiver _recver;
	messaging::Sender _sender;
	boost::shared_ptr<boost::thread> _thread;
	RpcRouteEndPointPtr _ep;
};

typedef boost::shared_ptr<QpidConnection> QpidConnectionPtr;

}

#endif


#endif
