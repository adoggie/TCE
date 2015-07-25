
#include "sock_conn.h"
#include "sock_adapter.h"
#include "../communicator.h"
#include "../message.h"
#include <iostream>
 #include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

namespace tce{

#define READ_BUFFSIZE  1024*5
#define WRITE_BUFFSIZE READ_BUFFSIZE
#define PACKET_HDRSIZE 14
#define MAX_PACKET_SIZE (1024*1024)

//QSocketConnection::QSocketConnection(QSocketAdapter* adapter):RpcConnection(""),_sock(RpcCommunicator::instance().ioservice() )
QSocketConnection::QSocketConnection():RpcConnection(""),_sock(RpcCommunicator::instance().ioservice() )

{
	//_adapter = adapter;
	boost::asio::socket_base::non_blocking_io command(true);
	//_sock.io_control( command );
	_type = SOCKET;
	reset();
	//_budyconn = shared_from_this();
}

QSocketConnection::QSocketConnection(const std::string& uri,const Properties_t& opts):
		RpcConnection(uri,opts),_sock(RpcCommunicator::instance().ioservice())
	{
	//QpidConnection *p = new QpidConnection(uri,opts);
	_type = SOCKET;
	reset();
	//_adapter = NULL;
//	_budyconn = shared_from_this();
}


QSocketConnection::~QSocketConnection(){
	std::cout<<"~QSocketConnection()"<<std::endl;
}

void QSocketConnection::reset(){

	boost::mutex::scoped_lock lockr(_mtxread);
	boost::mutex::scoped_lock lockw(_mtxwrite);
	_readbuf.clear();
	_writebufs.clear();
}

bool QSocketConnection::connect(){
	RpcConnection::connect();

	std::vector<std::string> params;
	boost::split( params,_uri,boost::is_any_of(": \t"),boost::token_compress_on);
	if(params.size()<2){
			return false;
		}

	try{
		boost::trim(params[0]);
		boost::trim(params[1]);
		boost::asio::ip::address addr =  boost::asio::ip::address::from_string( params[0]);
		uint16_t port;
		port = boost::lexical_cast<uint16_t>(params[1]);
		boost::asio::ip::tcp::endpoint ep(addr,port);

		if(0){
		//if(!sync){
			/*
			_sock.async_connect(ep,boost::bind(&RpcConnection::handle_connect,
					shared_from_this(),
					//this,
					boost::asio::placeholders::error
					));
					*/
		}else{
			boost::system::error_code ec;
			_sock.connect( ep,ec);
			if( ec){
				onFault(RpcConsts::RPCERROR_CONNECT_UNREACHABLE);
				reset();
				return false;
			}
			onConnected();
			doRead();
		}
	}catch(...){
		return false;
	}

	//this->_sock.get_io_service().poll();
	return true;
}

void QSocketConnection::handle_connect(const boost::system::error_code& ec){
	if( ec){
		try{
			onFault(RpcConsts::RPCERROR_CONNECT_UNREACHABLE);
			_sock.close();
		}catch(...){}
		return;
	}
	onConnected();
	doRead();  // invoke start() okay as well
	//start();
}

void QSocketConnection::close(){
	try{
		_sock.close();
	}catch(...){

	}
	//stop();
}

void QSocketConnection::destroy(){
	RpcConnection::destroy();
}

//必须再次发起连接，而且必须时同步连接
bool QSocketConnection::sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec){
	boost::shared_ptr<ByteArray> bytes;
	if( this->isConnected()== false){
		// try to connect with blocked
		if( connect() == false){
			ec = RpcConsts::RPCERROR_CONNECT_UNREACHABLE;
			return false;
		}
	}

	bytes = m->marshall();
	{
		boost::mutex::scoped_lock lockwrite(_mtxwrite);

		ByteArray hdr;
		hdr.writeUnsignedInt(0xEFD2BB99);
		hdr.writeUnsignedInt(bytes->size() + PACKET_HDRSIZE - 4);  //不包括 magic长度
		hdr.writeByte(RpcConsts::COMPRESS_NONE);
		hdr.writeByte(RpcConsts::ENCRYPT_NONE);
		hdr.writeUnsignedInt(0x00000100);
		size_t size;

		DataChunkPtr dc(new DataChunk);
		dc->resize( PACKET_HDRSIZE + bytes->size() );
		size = dc->size();
		//size = _writebuf.size();
	//	char * p = &_writebuf[size];

		//_writebuf.resize(_writebuf.size()+ PACKET_HDRSIZE + bytes->size());
		memcpy(&dc->at(0),hdr.data(),PACKET_HDRSIZE);
		memcpy(&dc->at(PACKET_HDRSIZE),bytes->data() ,  bytes->size() );
		_writebufs.push_back( dc);
	}
	//LOGTRACE("sendDetail..");
	doWrite();
	return true;
}

void QSocketConnection::start(){
	doRead();
	doWrite();
}

void QSocketConnection::stop(){
	boost::mutex::scoped_lock lock( _mtx);
	try{
		if( !this->isConnected() ){
			return;
		}
		_sock.close();
	}catch(...){}
	onDisconnected();
}


void QSocketConnection::onConnected(){
	RpcConnection::onConnected();
	{
		//_adapter->addConnection( shared_from_this());
		//this->attachAdapter(_adapter);
	}
}

bool QSocketConnection::isConnected(){
	return RpcConnection::isConnected();
}

void QSocketConnection::onDisconnected(){
	reset();
	RpcConnection::onDisconnected();
	if(_adapter){
		_adapter->removeConnection( shared_from_this());
		this->detachAdapter();

	}
}

void QSocketConnection::handle_write( DataChunkPtr dc,boost::system::error_code ec,size_t bytes_transferred){
	if(ec){
		stop();
		return; // 异常产生
	}
	//LOGTRACE("handle_Write..");
	{
		boost::mutex::scoped_lock lockwrite(_mtxwrite);
		if( bytes_transferred){
			DataChunkPtr ndc( new DataChunk(*dc));
			ndc->erase( ndc->begin(),ndc->begin() + bytes_transferred);
			if(ndc->size()){
				_writebufs.push_front(ndc);
			}
		}
	}
	doWrite();
	//start();
}

void QSocketConnection::handle_read(DataChunkPtr dc,const boost::system::error_code& ec,std::size_t bytes){
//	static int count=0;
	if(ec){
		stop();
		return;
	}
	LOGTRACE("handle_read..");
//	std::cout<< ++count <<std::endl;


	if( bytes){
		boost::mutex::scoped_lock lock(_mtxread);
		size_t size;
		//size = _readbuf.size();
	//	_readbuf.resize(size+bytes);
	//	memcpy(&_readbuf[size],&dc->at(0),bytes);  @@坑爹的东西，当vector方式用了，郁闷,还是用vector的好
		_readbuf.insert(_readbuf.end(),dc->begin(),dc->begin()+ bytes);

		int r = false;
		size = _readbuf.size();
		DataBuffers dbfs;

		r = parseData(&_readbuf[0],size,dbfs);
		std::cout<< "parseData result:"<<r<<std::endl;

		if( r == -1){
			close();
			return;
		}else if( r == 0){



			goto _NEXT;; // need more
		}

		size_t consumed = _readbuf.size() - size;
		//consumed = _readbuf.size();
		if( consumed){
			//std::cout<<"consumed size:"<<consumed<<" buf size:"<<_readbuf.size()<<std::endl;
			_readbuf.erase(_readbuf.begin(),_readbuf.begin()+consumed);

		}
		DataBuffers::iterator itr;
		for(itr = dbfs.begin();itr!=dbfs.end();itr++){
			boost::shared_ptr<RpcMessage> m = RpcMessage::unmarshall(*(*itr));
			if(!m.get()){
				//stop();
				close();
				return;
			}
			m->user_id = _userid;
			m->conn = shared_from_this();
			LOGTRACE("enqueueMsg()");
			RpcCommunicator::instance().enqueueMsg(m);
			//LOGTRACE("enqueueMsg..");
		}
	}else{
		LOGTRACE("read byte is 0");
	}

_NEXT:
	doRead();
	//LOGTRACE("handle_read end..");
}



// >=1 - ok(consumed   bytes) , 0 - need more, -1: data dirty
int QSocketConnection::parseData(const char *  d,size_t& dsize,DataBuffers& dbfs){
//	int r = 1;
	const char  * p1;
	p1 = d;
//	size_t orgsize = dsize;
	while(dsize > 0){
		if(dsize < PACKET_HDRSIZE){
			return 0;
		}
		ByteArray bytes(d,PACKET_HDRSIZE);
		uint32_t magic;
		uint32_t size;
		uint8_t compress,encrypt;
		uint32_t version;
		magic = bytes.readUnsignedInt();
		size = bytes.readUnsignedInt();
		compress = bytes.readByte();
		encrypt = bytes.readByte();
		version = bytes.readUnsignedInt();

		if( 0xEFD2BB99!= magic){
			return -1;
		}
		if(size > MAX_PACKET_SIZE){
			return -1;
		}
		if(size<=10){
			return -1; // dirty
		}
		if( dsize < size+4 ){
			return 0;
		}
		boost::shared_ptr<ByteArray> b( new ByteArray( d+ PACKET_HDRSIZE,size-PACKET_HDRSIZE+4) );
		dbfs.push_back(b);
		d+= size+4;
		dsize-=size+4;
	}

	return 1;
}

bool QSocketConnection::doRead(){
	//读数据，解码，投入communicator的消息队列

	//recycled
	try{
	//	LOGTRACE("doRead..");
	DataChunkPtr dc(new DataChunk(READ_BUFFSIZE));

	_sock.async_read_some( boost::asio::buffer(*dc,dc->size() ),
			boost::bind(&RpcConnection::handle_read, // shared_from_this()定义在基类，没法子，只能透过需函数传递到这里
					//boost::enable_shared_from_this<QSocketConnection>::shared_from_this(),
					shared_from_this(), dc,boost::asio::placeholders::error,boost::asio::placeholders::bytes_transferred));
	}catch(...){
		LOGTRACE("doread error...");
		return false;
	}
	return true;
}

bool  QSocketConnection::doWrite(){

	boost::mutex::scoped_lock lockwrite(_mtxwrite);
	//LOGTRACE("doWrite..");
	size_t size;
	size = WRITE_BUFFSIZE;

	if(_writebufs.size() == 0){
		doRead();
		return true;
	}
	DataChunkPtr dc = *_writebufs.begin();

	_writebufs.pop_front();
	//boost::asio::const_buffers_1 bf( &dc->at(0),dc->size());
	try{
	_sock.async_write_some(boost::asio::buffer(*dc,dc->size()),boost::bind(&RpcConnection::handle_write,shared_from_this(),dc,boost::asio::placeholders::error,boost::asio::placeholders::bytes_transferred));
	//	_sock.async_write_some(bf,boost::bind(&QSocketConnection::handle_write,shared_from_this(),dc,boost::asio::placeholders::error,boost::asio::placeholders::bytes_transferred));
	}catch(...){
		LOGTRACE("dowrite error...");
		return false;
	}
	return true;
}



}
