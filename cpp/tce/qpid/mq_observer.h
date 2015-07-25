

#ifndef _MQ_SET_H
#define _MQ_SET_H



#include "../observer.h"

namespace tce{

namespace mqroute{

class MsgObserver_MQ:public MessageObserver{
public:
	int onMessageGet( RpcMessagePtr& msg);
	int onMessagePut( RpcMessagePtr& msg);
};

typedef boost::shared_ptr<MsgObserver_MQ> MsgObserver_MQPtr;




} // mqroute

} // namespace tce



#endif
