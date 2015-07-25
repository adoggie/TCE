
#include "message.h"

#include "communicator.h"

#include "exception.h"

#include <boost/foreach.hpp>

namespace tce{



boost::shared_ptr<ByteArray> RpcMessage::marshall(){
	//TRACECONTEXT<< "RpcMessage::marshall()";
	boost::shared_ptr<ByteArray> stream(new ByteArray);
	//stream->writeUnsignedInt(0xECBBEEDD);
	stream->writeByte(this->type);
	stream->writeUnsignedInt(this->sequence);
	stream->writeByte(this->calltype);
	stream->writeShort((int16_t)this->ifidx);
	stream->writeShort((int8_t)this->opidx);
	stream->writeInt( this->errcode);
	stream->writeByte( (int8_t)this->paramsize); //参数个数
	stream->writeShort((int16_t) this->call_id);
	this->extra.marshall(*stream.get());
	
//	std::list< boost::shared_ptr<ByteArray> >::iterator itr;
//	for(itr=this->params.begin();itr!= params.end();itr++){
//		stream->writeBytes( *(*itr));
//	}
	stream->writeBytes(paramstream );
	return stream;
}

boost::shared_ptr<RpcMessage> RpcMessage::unmarshall(ByteArray & d){
	//TRACECONTEXT<< "RpcMessage::unmarshall()";

	boost::shared_ptr<RpcMessage> m (new RpcMessage);
	try{
		m->type = d.readByte();
		m->sequence = d.readUnsignedInt();
		m->calltype = d.readByte();
		m->ifidx = (uint16_t)d.readShort();
		m->opidx = (uint16_t)d.readShort();
		m->errcode = d.readInt();
		m->paramsize = d.readByte();
		m->call_id = d.readShort();
		
		if(!m->extra.unmarshall( d) ){
			return RpcMessagePtr();
		}
//		d.next( (int)m->extra.datasize());
		m->paramstream.writeBytes2(d,d.position(),d.remain());
	}catch(RpcException &e ){
		LOGTRACE( e.what() );
		return RpcMessagePtr();
	}
	return m;
}


//--------------------------------------------------------

RpcMessageCall::RpcMessageCall(uint8_t flags ){
	this->calltype = CALL | flags;
	this->sequence = RpcCommunicator::instance().getUniqueSequence();
}


//--------------------------------------------------------

RpcMessageReturn::RpcMessageReturn(uint8_t flags){
	this->calltype = RETURN | flags;
}


}
