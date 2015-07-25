
#ifndef _TCE_QPID_H
#define _TCE_QPID_H

#include "../base.h"
//#include "qpid_conn.h"
#include "ep.h"

namespace tce{

//namespace mqroute{

#define IF_IDX uint16_t
#define EP_IDX uint16_t

struct QMssageAttribute_t:public TceDelta{
	uint16_t		src_type;	///<发送源类型
	uint16_t		src_idx;	///<发送源编号
//	uint8_t		dest_type;	///<目标类型
//	uint8_t 	dest_idx;	///<目标编号
//	uint8_t		conn_type;	///<发送源的连接类型 RpcConnection::SOCKET/QPID
//	uint32_t	issue_time;	///<创建时间
	uint64_t	user_id;	///<线路用户或设备编号 ,Connectinon中添加一个属性，

	/// mq到socket的消息也自动完成传递,这种对于socket发起到mq内部系统的请求返回，处理可以实现
	///< 内部系统主动发起对设备链接，这个需要依赖上层应用接口来控制了
	///< 最好在socket的Connection中添加一个线路id，用来标识一路用户的链接，此id未具体应用产生的，
	///.A接收到C的返回,最好在Rpc消息中添加64位的属性用于保存应用属性,这个应用属性在用户Rpc调用时通过RpcExtraData传递到底部
	///设备链接上gwa之后，通过认证获取一个uid，将uid设置为gwa端的Connection的属性，当内部发起调用设备时，通过
	///extraData携带设备属性到rpc层，并传递到gwa，gwa解出这个id，并寻找匹配的uid，找到，则在此链接上将rpc包转发出去
	///=================================================================================
	///2.C要接收到A的返回，可配置route表，或者通过token直接发送到接收队列
	///3.C到A的调用请求，C调用时传递设备编号到conn_id，B根据编号自动将消息转发到A
	///4.A到C的调用请求，B转换消息时，将A链接的编号作为conn_id传递到C
	/// C返回时，根据src_type,src_idx找出mq名称,将conn_id回塞到B,B再找出A的链接，发送到A，conn通过queues属性带回到B
	///
	///1. C主动发起对A的请求时，调用函数需要带入设备编号到extradata
	///那就不许要往extradata中塞属性了
};
typedef boost::shared_ptr<QMssageAttribute_t> QMssageAttributePtr;


struct Interface_t{
	uint16_t ifidx;			///<接口编号
	std::string name ;		///<接口名称 (直接idl中定义的名称)
};
typedef boost::shared_ptr<Interface_t> InterfacePtr;

struct Service_t{
	uint16_t	id;					///<服务类型编号
	std::string name; 				///<服务名称
	std::string mq_pattern;			///< mq_pattern
	std::map< uint16_t,boost::shared_ptr<Interface_t> > ifs; 	///<接口列表
	bool if_exist(uint16_t ifx){
		return  ifs.find(ifx) != ifs.end();
	}
};
typedef boost::shared_ptr<Service_t> ServicePtr;

typedef std::string RouteDest_t;
typedef std::vector<RouteDest_t> RouteDestList_t;


struct RouteInOutPair_t{
	//std::vector<RpcRouteEndPointPtr> ins;
	//std::vector<RpcRouteEndPointPtr> outs;
	RpcRouteEndPointPtr in;
	RpcRouteEndPointPtr out;
	std::string token_redirect;
};
typedef boost::shared_ptr<RouteInOutPair_t> RouteInOutPairPtr;

struct RouteDetail_t{
	InterfacePtr ifx;
	std::map<EP_IDX,RouteInOutPairPtr> calls; //以in作为索引
//	std::map<std::string,RpcRouteEndPointPtr> names_eps;
	std::map<EP_IDX,RouteInOutPairPtr> returns;
	RouteDetail_t(){
//		token_check = false;
	}
	RouteInOutPairPtr getOutEndpointOfCall(EP_IDX epin){
		std::map<EP_IDX,RouteInOutPairPtr>::iterator itr;
		itr =calls.find(epin);
		if(  itr== calls.end() ){
			return RouteInOutPairPtr();
		}
		return itr->second;

	}
	RouteInOutPairPtr getOutEndpointOfReturn(EP_IDX epin){
		std::map<EP_IDX,RouteInOutPairPtr>::iterator itr;
		itr =returns.find(epin);
		if(  itr== returns.end() ){
			return RouteInOutPairPtr();
		}
		return itr->second;
	}
//	RpcRouteEndPointPtr getEndpointWithName(const std::string & name);
};
typedef boost::shared_ptr<RouteDetail_t> RouteDetailPtr;

struct ServerDeatil_t{
	uint16_t	id;		///<服务器编号
	std::string name;	///<服务器名称
	ServicePtr service;	///<类型
	Properties_t props;	///<属性

	std::map<IF_IDX, RouteDetailPtr > routes;	///<路由定义信息
	std::map<EP_IDX ,RpcRouteEndPointPtr > id_eps; ///端点集合
	std::map<std::string ,RpcRouteEndPointPtr > name_eps; ///端点集合

	std::map<std::string , RpcRouteEndPointPtr> mq_reads;//额外的读队列
	std::map<std::string , RpcRouteEndPointPtr> mq_writes;//额外的写队列

	RpcRouteEndPointPtr findOutEnpoint(const std::string& name){
		if( name_eps.find(name) != name_eps.end() ){
			return name_eps[name];
		}
		return RpcRouteEndPointPtr();
	}

	std::vector<RpcRouteEndPointPtr> getReadableEndpoints(){
		std::vector<RpcRouteEndPointPtr>  res;
		std::map<std::string , RpcRouteEndPointPtr>::iterator itr;
		for(itr=mq_reads.begin();itr!= mq_reads.end(); itr++){
			RpcRouteEndPointPtr& ep = itr->second;
			if( ep->type == RpcConnection::SOCKET || ep->type == RpcConnection::MQ || ep->type == RpcConnection::WEBSOCKET){
				res.push_back(ep);
			}
		}
		return res;
	}


	RouteInOutPairPtr  findOutRouteInOutPair(IF_IDX ifidx,int calltype,EP_IDX ep_in){
		RpcRouteEndPointPtr ep;
		std::map<IF_IDX, RouteDetailPtr >::iterator itrRoutes;
		itrRoutes = routes.find(ifidx);
		if(itrRoutes == routes.end()){
			return RouteInOutPairPtr();
		}
		RouteDetailPtr & if_route = itrRoutes->second;
		RouteInOutPairPtr inout;
		if( calltype & RpcMessage::CALL){
			inout = if_route->getOutEndpointOfCall(ep_in);
		}else{
			inout = if_route->getOutEndpointOfReturn(ep_in);
		}
		return inout;
	}
};
typedef boost::shared_ptr<ServerDeatil_t>  ServerDetailPtr;

//token路由信息
struct RouteToken_t{
	//std::string
};


}

#endif
