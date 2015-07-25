
#ifndef _MQ_SET_H
#define _MQ_SET_H

#include <tce/tce.h>
#include "../utils/singleton.h"
#include  "qpid_conn.h"
#include "mq.h"
#include "../observer.h"
#include <boost/enable_shared_from_this.hpp>
namespace tce{

class MqSet:public MessageObserver,public boost::enable_shared_from_this<MqSet> {
public:
	MqSet();
	struct Properites_t{
		bool reconnect;
	};

	bool init(const std::string& svcname,const std::string & ifsvc, const Properites_t& props=Properites_t()); //接口定义文件

	bool postMessage(boost::shared_ptr<RpcMessage>& m); //直接发送，底部通过映射表转换
	void routeMessage(const std::string & mq,RpcContext* ctx); //设置下一站路由队列方向

	//void addServant(const std::string& name,const boost::shared_ptr<RpcServant>& servant );
	RpcCommAdapterPtr getAdapterWithEndpiontName(const std::string& name) ;//
	ServerDetailPtr& server(){ return _localserver;}
protected:
	int onMessageGet( RpcMessagePtr& msg);				///<截获收到的Rpc消息
	int onMessagePut( RpcMessagePtr& msg);				///<截获即将要发送的Rpc消息，准备一次路由
private:
	bool postMessageIntoQueue(const std::string& mq,RpcMessagePtr& msg);
	int onMessageGet_Socket(RpcMessagePtr& msg);  		///<从socket上接收的数据
	int onMessageGet_Mq(RpcMessagePtr& msg);
	bool isLocalInterface(uint16_t ifidx);				///<检测是否是本地接口
	bool isLocalMessage(const RpcMessagePtr& m);		///<检测是否是本地接收消息
	bool run();
public:

	std::string getRouteMqFromToken(const RpcMessagePtr& msg); //从token中获取发送mq的名称
	RpcRouteEndPointPtr getRouteEndpointWithMqAttr(uint16_t src_type,uint16_t src_id); //根据 mq属性包 src_type,src_id找出mq名称
public:
	ServerDetailPtr& localserver(){ return _localserver;}
private:
	Properites_t _props;
	ServerDetailPtr _localserver;

	std::map<uint16_t,ServicePtr> _id_svcdefs;			///<系统所有服务系统类型
	std::map<std::string ,ServicePtr > _name_svcdefs;
};



} // namespace tce

#define mqset_inst() tce::Singleton<tce::MqSet>::instance()



#endif

