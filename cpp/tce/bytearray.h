
#ifndef _UTILS_BYTEARRAY_H
#define _UTILS_BYTEARRAY_H

#include <boost/thread/mutex.hpp>

#include "base.h"
#include "exception.h"
#include <vector>
#include <string>

#include <arpa/inet.h>
#include <string.h>

namespace tce{

inline
uint64_t ntohl64(uint64_t arg64){

  uint64_t res64;

#if __LITTLE_ENDIAN
  uint32_t low = (uint32_t) (arg64 & 0x00000000FFFFFFFFLL);
  uint32_t high = (uint32_t) ((arg64 & 0xFFFFFFFF00000000LL) >> 32);

  low = ntohl(low);
  high = ntohl(high);

  res64 = (uint64_t) high + (((uint64_t) low) << 32);
#else
  res64 = arg64;
#endif

  return res64;

}

inline
uint64_t htonl64(uint64_t arg64){

  uint64_t res64;

#if __LITTLE_ENDIAN
  uint32_t low = (uint32_t) (arg64 & 0x00000000FFFFFFFFLL);
  uint32_t high = (uint32_t) ((arg64 & 0xFFFFFFFF00000000LL) >> 32);

  low = htonl(low);
  high = htonl(high);

  res64 = (uint64_t) high + (((uint64_t) low) << 32);
#else
  res64 = arg64;
#endif

  return res64;
}



class ByteArray{
protected:
	std::vector<uint8_t> _bytes;
	size_t _pos; //当前位置
public:

	ByteArray(){
		reset();
	}

	ByteArray(const char* data,size_t size){
		reset();
		_bytes.resize(size);
		_bytes.assign((uint8_t*)data,(uint8_t*)(data+size) );

	}

	size_t size() const{
		return _bytes.size();
	}

	char * data(){
		return (char*)&_bytes[0];
	}

	void reset(){
		_bytes.clear();
		_pos = 0;
	}

	void position(int pos){
		_pos = pos;
	}

	int remain(){
		return size() - _pos;
	}

	void next(int p){
		_pos+=p;
	}

	int position() const{
		return _pos;
	}

	void writeByte(uint8_t val) throw (RpcException){
		_bytes.push_back(val);
	}

	void writeShort(int16_t val) throw (RpcException){
		val = htons(val);
		_bytes.resize(_bytes.size() + 2);
		memcpy(&_bytes[_bytes.size()-2],&val,2);
	}

	void writeInt(int32_t val) throw (RpcException){
		val = htonl(val);
		_bytes.resize(_bytes.size() + 4);
		memcpy(&_bytes[_bytes.size()-4],&val,4);
	}

	void writeUnsignedInt(uint32_t val) throw (RpcException){
		writeInt((int32_t)val);
	}

	void writeInt64(int64_t& val) throw(RpcException){
		val= htonl64(val);
		_bytes.resize(_bytes.size() + 8);
		memcpy(&_bytes[_bytes.size()-8],&val,8);
	}

	void writeFloat(float val) throw(RpcException){
		int v ;
		memcpy(&v,&val,4);
		writeInt(v);
	}

	void writeDouble(double val) throw(RpcException){
		int64_t v;
		memcpy(&v,&val,8);
		_bytes.resize(_bytes.size() + 8);
		memcpy(&_bytes[_bytes.size()-8],&v,8);
	}

	void writeString(const std::string& d) throw(RpcException){
		size_t size = d.size();
		this->writeInt((int32_t)size);
		_bytes.resize(_bytes.size()+size);
		memcpy(&_bytes[_bytes.size() - size],(uint8_t*)d.c_str(),size);

	}

	void writeBytes(const ByteArray& d) throw(RpcException){
		size_t size = d.size();

		_bytes.resize(_bytes.size()+size);
		memcpy(&_bytes[_bytes.size() - size],&d._bytes[0],size);
	}

	void writeBytes2(const ByteArray& d,int pos,size_t size ) throw(RpcException){
		_bytes.resize(_bytes.size()+size);
		memcpy(&_bytes[_bytes.size() - size],&d._bytes[pos],size);
	}

	void writeBytes3(const char* d,size_t size ) throw(RpcException){
		_bytes.resize(_bytes.size()+size);
		memcpy(&_bytes[_bytes.size() - size],d,size);
	}

/*
	void writeBytes(const ByteArray& d,size_t pos,size_t len) throw(RpcException){
		size_t size = _bytes.size();
		_bytes.resize(_bytes.size()+size);
		memcpy(&_bytes[_bytes.size() - size],&d._bytes[0],d._bytes.size());
	}
*/
	uint8_t readByte() throw (RpcException){
		uint8_t r;
		if(_pos+1  > _bytes.size() ){
			throw RpcException(RpcConsts::RPCERROR_DATA_INSUFFICIENT);
		}
		r = _bytes[_pos];
		_pos+=1;
		return r;
	}

	int16_t readShort() throw (RpcException){
		uint16_t r;
		if(_pos+ 2  > _bytes.size() ){
			throw RpcException(RpcConsts::RPCERROR_DATA_INSUFFICIENT);
		}
		memcpy(&r,&_bytes[_pos],2);
		r = ntohs(r);
		_pos+=2;
		return r;
	}

	int32_t readInt() throw (RpcException){
		int32_t r;
		if(_pos+ 4  > _bytes.size() ){
			throw RpcException(RpcConsts::RPCERROR_DATA_INSUFFICIENT);
		}
		memcpy(&r,&_bytes[_pos],4);
		r = ntohl(r);
		_pos+=4;
		return r;
	}

	uint32_t readUnsignedInt() throw (RpcException){
		uint32_t r;
		r = (uint32_t) readInt();
		return r;
	}

	int64_t readInt64() throw(RpcException){
		int64_t r;
		if(_pos+ 8  >_bytes.size() ){
			throw RpcException(RpcConsts::RPCERROR_DATA_INSUFFICIENT);
		}
		memcpy(&r,&_bytes[_pos],8);
		r =(int64_t) ntohl64((uint64_t)r);
		_pos+=8;
		return r;
	}

	float readFloat() throw(RpcException){
		float r;
		int32_t ir;
		ir = readInt();
		memcpy(&r,&ir,4);
		return r;
	}

	double readDouble() throw(RpcException){
		double r;
		int64_t i64;
		i64 = readInt64();
		memcpy(&r,&i64,8);
		return r;
	}

	std::string readString() throw(RpcException){
		std::string r;
		int32_t size;
		size = readInt();

		if(_pos+ size  > _bytes.size() ){
			throw RpcException(RpcConsts::RPCERROR_DATA_INSUFFICIENT);
		}
		r.assign((char*)&_bytes[_pos],size);
		_pos+=size;

		return r;
	}



};

typedef boost::shared_ptr<ByteArray> ByteArrayPtr;

}

#endif

