
#ifndef _TCE_RPC_EXCEPTION_H
#define _TCE_RPC_EXCEPTION_H


#include "base.h"

#include <string>

namespace tce{

struct RpcException{
	RpcException(RpcConsts::ErrorCode code_,int subcode_=0,const std::string & msg_="" ){
		errcode = code_;
		subcode = subcode_;
		msg = msg_;
	}

	std::string what() const{
		RpcConsts::error_info_t * err = NULL;
		err = RpcConsts::get_error(errcode);
		if(err){
			return err->str;
		}
		return "unRegistered error";
	}

	int errcode;
	int subcode;
	std::string msg;
};

}

#endif
