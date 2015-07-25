
#ifdef _WEBSOCKET

#include "websocket_conn.h"
#include "websocket_adapter.h"
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
WebSocketConnection::WebSocketConnection():RpcConnection(""){
	_type = WEBSOCKET;
	reset();
}

WebSocketConnection::WebSocketConnection(const std::string& uri,const Properties_t& opts):
		RpcConnection(uri,opts){
	_type = WEBSOCKET;
	reset();
}



bool WebSocketConnection::connect(){
	return RpcConnection::connect();

}



void WebSocketConnection::close(){
	try{
	//	_sock.close();
		_conn->close(websocketpp::close::status::GOING_AWAY);
	}catch(...){

	}
	//stop();
}

void WebSocketConnection::destroy(){
	RpcConnection::destroy();
}

//必须再次发起连接，而且必须时同步连接
bool WebSocketConnection::sendDetail(const boost::shared_ptr<RpcMessage>& m,RpcConsts::ErrorCode &ec){
	boost::shared_ptr<ByteArray> bytes;
	if( this->isConnected()== false){
		// try to connect with blocked
//		if( connect(true) == false){
//			ec = RpcConsts::RPCERROR_CONNECT_UNREACHABLE;
//			return false;
//		}
	}

	bytes = m->marshall();
	{
		//boost::mutex::scoped_lock lockwrite(_mtxwrite);

		ByteArray hdr;
		hdr.writeUnsignedInt(0xEFD2BB99);
		hdr.writeUnsignedInt(bytes->size() + PACKET_HDRSIZE - 4);  //不包括 magic长度
		hdr.writeByte(RpcConsts::COMPRESS_NONE);
		hdr.writeByte(RpcConsts::ENCRYPT_NONE);
		hdr.writeUnsignedInt(0x00000100);
//		size_t size;

		//DataChunkPtr dc(new DataChunk);
		DataChunk dc;
		dc.resize( PACKET_HDRSIZE + bytes->size() );
//		size = dc->size();
		memcpy(&dc.at(0),hdr.data(),PACKET_HDRSIZE);
		memcpy(&dc.at(PACKET_HDRSIZE),bytes->data() ,  bytes->size() );
//		_writebufs.push_back( dc);
		std::string payload;
		payload.append( &dc.at(0),&dc.at(0)+ dc.size());
		_conn->send(payload,websocketpp::frame::opcode::BINARY);
	}
	//LOGTRACE("sendDetail..");
	return true;
}



void WebSocketConnection::onConnected(){
	RpcConnection::onConnected();
	{
		//_adapter->addConnection( shared_from_this());
		//this->attachAdapter(_adapter);
	}
}

bool WebSocketConnection::isConnected(){
	return RpcConnection::isConnected();
}

void WebSocketConnection::onDisconnected(){
	RpcConnection::onDisconnected();
	if(_adapter){
		_adapter->removeConnection( shared_from_this());
		this->detachAdapter();
	}
}


// >=1 - ok(consumed   bytes) , 0 - need more, -1: data dirty
int WebSocketConnection::parseData(const char *  d,size_t& dsize,DataBuffers& dbfs){
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

void WebSocketConnection::onMessage(websocketpp::message::data_ptr msg){
	std::string  d = msg->get_payload();
	int code = msg->get_opcode();

	log_debug(LOGTCE,"websocket.onMessage: code=%d,const_size=%d,content=%s",%code%d.size()%d);
	if( d.size()){
		size_t size;
		_readbuf.insert(_readbuf.end(),d.c_str(),d.c_str()+ d.size());

		int r = false;
		size = _readbuf.size();
		DataBuffers dbfs;

		r = parseData(&_readbuf[0],size,dbfs);
		std::cout<< "parseData result:"<<r<<std::endl;

		if( r == -1){
			close();
			return;
		}else if( r == 0){
			return;
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


}


void WebSocketConnection::reset(){

}

}


#endif
