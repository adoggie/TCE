
#ifndef _RPC_EXTRADATA_H
#define _RPC_EXTRADATA_H

#include "base.h"
#include "bytearray.h"
#include <boost/shared_ptr.hpp>

#include "message.h"

namespace tce{


class RpcMsgFilter{

protected:
	virtual ~RpcMsgFilter() =0;
public:
	// 0 - no taken ; 1 - taken and outer not care
	virtual int filter(const boost::shared_ptr<RpcMessage>& msg);
	
	
};


}


#endif

