
#ifndef _MSG_OBSERVER_H
#define _MSG_OBSERVER_H

#include "base.h"
#include "message.h"

namespace tce{
//消息观察者

struct MessageObserver{
public:
	virtual ~MessageObserver() = 0;
	// 0 - do nothing ; 1 - consumed ,outter should not do anythin again.
	virtual int onMessageGet( RpcMessagePtr& msg)=0;
	virtual int onMessagePut( RpcMessagePtr& msg)=0;
};
inline
MessageObserver::~MessageObserver(){}

typedef boost::shared_ptr<MessageObserver> MessageObserverPtr;

#define MSG_IGNORED 0
#define MSG_CONTINUE MSG_IGNORED
#define MSG_CONSUMED 1
#define MSG_DROPPED MSG_CONSUMED


}

#endif

