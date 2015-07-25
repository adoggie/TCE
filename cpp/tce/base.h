
#ifndef _RPC_BASE_H
#define _RPC_BASE_H

//#include "bytearray.h"

#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <list>
#include <deque>

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/utility.hpp>
#include <boost/format.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>



namespace tce{

struct RpcConsts{
	enum ErrorCode{
		RPCERROR_SUCC = 0,
		RPCERROR_SENDFAILED =1,
		RPCERROR_DATADIRTY= 3,
		RPCERROR_TIMEOUT = 2,
		RPCERROR_INTERFACE_NOTFOUND = 4,
		RPCERROR_UNSERIALIZE_FAILED = 5,
		RPCERROR_REMOTEMETHOD_EXCEPTION = 6,
		RPCERROR_DATA_INSUFFICIENT = 7,
		RPCERROR_REMOTE_EXCEPTION = 8,

		RPCERROR_CONNECT_UNREACHABLE = 101,
		RPCERROR_CONNECT_FAILED  = 102,
		RPCERROR_CONNECT_REJECT = 103,
		RPCERROR_CONNECTION_LOST = 104	//连接丢失
	};

	struct error_info_t{
		int code;
		const char* str;
	};

	static error_info_t* get_error(int ec){
		static error_info_t _errors[]={
				{RPCERROR_SENDFAILED,"RPCERROR_SENDFAILED"},
				{RPCERROR_DATADIRTY,"RPCERROR_DATADIRTY"},
				{RPCERROR_TIMEOUT,"RPCERROR_TIMEOUT"},
				{RPCERROR_INTERFACE_NOTFOUND,"RPCERROR_INTERFACE_NOTFOUND"},
				{RPCERROR_UNSERIALIZE_FAILED,"RPCERROR_UNSERIALIZE_FAILED"},
				{RPCERROR_REMOTEMETHOD_EXCEPTION,"RPCERROR_REMOTEMETHOD_EXCEPTION"},
				{RPCERROR_DATA_INSUFFICIENT,"RPCERROR_DATA_INSUFFICIENT"},
				{RPCERROR_REMOTE_EXCEPTION,"RPCERROR_REMOTE_EXCEPTION"},

				{RPCERROR_CONNECT_UNREACHABLE,"RPCERROR_CONNECT_UNREACHABLE"},
				{RPCERROR_CONNECT_FAILED,"RPCERROR_CONNECT_FAILED"},
				{RPCERROR_CONNECT_REJECT,"RPCERROR_CONNECT_REJECT"},
				{RPCERROR_CONNECTION_LOST,"RPCERROR_CONNECTION_LOST"},
				{-1,NULL},
			};

		error_info_t * err = NULL;
		size_t n= 0;
		for(;n< sizeof(_errors)/sizeof(error_info_t);n++){
			if( _errors[n].str == NULL){
				break;
			}
			if( _errors[n].code == ec){
				err = &_errors[n];
				break;
			}
		}
		return err;
	}



	enum CompressType{
		COMPRESS_NONE = 0, //	#压缩方式ß
		COMPRESS_ZLIB = 1,
		COMPRESS_BZIP2 = 2,
	};

	enum EncryptType{
		ENCRYPT_NONE = 0,  // #加密方式
		ENCRYPT_MD5  = 1,
		ENCRYPT_DES  = 2,
	};

	enum MsgType{
		MSGTYPE_RPC = 1,
		MSGTYPE_NORPC = 2
	};

};

#define _X64 1

#ifdef _X64
	typedef long int64_t;
#else
	typedef long long int64_t;
#endif

	/*
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef unsigned short uint16_t;


typedef char int8_t;
typedef int int32_t;
typedef short int16_t;

*/

//#define __BYTE_ORDER 1
//#define __LITTLE_ENDIAN 1

typedef std::map<std::string,std::string> Properties_t;


#include <boost/thread/mutex.hpp>

//#include <boost/algorithm/string.hpp>


struct TraceContext{
	std::list<std::string> stacks; //Ë∞ÉÁî®Ê†à
	boost::mutex mtx;

	TraceContext& operator << (const std::string& where){
		boost::mutex::scoped_lock(mtx);
		stacks.push_back(where);
		return *this;
	}

	//Âà†Èô§ÊúÄËøëÊó•ÂøóÈ°π
	TraceContext& operator >> (int n){
		boost::mutex::scoped_lock(mtx);
		while( stacks.size()){
			stacks.pop_back();
		}
		return *this;
	}

	std::string traceback(){
		boost::mutex::scoped_lock(mtx);
	//	return boost::algorithm::join(stacks," >> ");
		return "";
	}

	void clear(){
		boost::mutex::scoped_lock(mtx);
		stacks.clear();
	}

};


struct TraceContextHelper{
	TraceContext* ctx;
	TraceContextHelper(TraceContext* ctx_){
		ctx = ctx_;
	}

	void operator<<(const std::string& s){
		(*ctx)<<s;
	}

	~TraceContextHelper(){
		(*ctx) >> 1;
	}
};


typedef std::vector<char> DataChunk;
typedef boost::shared_ptr<DataChunk> DataChunkPtr;
typedef std::list< DataChunkPtr > DataChunkList;


inline void SLEEP_MSEC(int n){boost::this_thread::sleep( boost::posix_time::microseconds(n) );}
inline  void SLEEP_SEC(int n){ boost::this_thread::sleep( boost::posix_time::seconds(n) );}

struct TceDelta{
	virtual ~TceDelta(){};
	int type;
	TceDelta(){
		type = NULL;
	}
};
//inline
//TceDelta::~TceDelta(){}
typedef boost::shared_ptr<TceDelta> TceDeltaPtr;


enum AccessFlags{
	AF_READ = 0x01,
	AF_WRITE = 0x02
};

typedef std::map<std::string,std::string> RpcProperites_t;
#define EXTR_NULL RpcProperites_t()

}


#endif
