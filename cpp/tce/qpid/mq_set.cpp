#include "mq_set.h"

#include "qpid_conn.h"

#include "../tinyxml/tinystr.h"
#include "../tinyxml/tinyxml.h"
#include "../communicator.h"
#include "../utils/logger.h"
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>

namespace tce {

//namespace mqroute{

MqSet::MqSet() {

}

/**
 * @param ifsvc - 消息路由映射配置文件
 *
 */
bool MqSet::init(const std::string& svcname, const std::string & ifsvc,
		const Properites_t& props) {
	TiXmlDocument doc;
	std::string xml;
	if (!doc.LoadFile(ifsvc.c_str())) {
		log_error(LOGTCE, "MqSet:: load file :%s failed!", %ifsvc);
		return false;
	}
	TiXmlElement* e = doc.RootElement();
	TiXmlElement* e2, *e3, *e4 = NULL;
	std::string tag, attr, text;
//	std::string localname; //

	tag = e->Value();
	if (tag != "SNS") {
		log_error(LOGTCE, "unknown xml file: %s ,Root-Tag:%s", %ifsvc%tag);
		return false;
	}

	std::map<std::string, RpcRouteEndPointPtr> eps;

	std::map<uint16_t, InterfacePtr> id_ifdefs;		///<系统所有接口表
	std::map<std::string, InterfacePtr> name_ifdefs;
	std::map<uint16_t, ServicePtr> id_svcdefs;			///<系统所有服务系统类型
	std::map<std::string, ServicePtr> name_svcdefs;

	e = e->FirstChildElement();
	while (e) {
		tag = e->Value();
		if (tag == "InterfaceDef") {
			e2 = e->FirstChildElement();
			while (e2) {
				tag = e2->Value();
				if (tag == "if") {
					boost::shared_ptr<Interface_t> ifce(new Interface_t);
					ifce->ifidx = boost::lexical_cast<uint16_t>(
							e2->Attribute("id"));
					ifce->name = e2->Attribute("name");
					id_ifdefs[ifce->ifidx] = ifce;
					name_ifdefs[ifce->name] = ifce;
				}
				e2 = e2->NextSiblingElement();
			}
		} else if (tag == "ServiceDef") {
			e2 = e->FirstChildElement();
			while (e2) {
				tag = e2->Value();
				if (tag == "service") {
					boost::shared_ptr<Service_t> svc(new Service_t);
					svc->id = boost::lexical_cast<uint16_t>(
							e2->Attribute("id"));
					svc->name = e2->Attribute("name");
					svc->mq_pattern = e2->Attribute("name");
					if (svc->mq_pattern == "") {
						log_error(LOGTCE,
								"interface < %s >'s mq_pattern  undefined!",
								%svc->name);
						return false;
					}
					e3 = e2->FirstChildElement("interfaces");
					while (e3) {
						e4 = e3->FirstChildElement();
						while (e4) {
							tag = e4->Value();
							if (tag == "if") {
								attr = e4->Attribute("name");
								std::map<std::string, InterfacePtr>::iterator itr;
								itr = name_ifdefs.find(attr);
								if (itr != name_ifdefs.end()) {
									svc->ifs[itr->second->ifidx] = itr->second;
								} else {
									log_error(LOGTCE,
											"interface < %s > undefined!",
											%attr);
									return false;
								}
							}
							e4 = e4->NextSiblingElement();
						}
						e3 = e3->NextSiblingElement();
					}
					id_svcdefs[svc->id] = svc;
					name_svcdefs[svc->name] = svc;
				}
				e2 = e2->NextSiblingElement();
			}			// end while{}
		} else if (tag == "EndPoints") {
			e2 = e->FirstChildElement("ep");
			size_t idx = 1;
			while (e2) {

				RpcRouteEndPointPtr ep(new RpcRouteEndPoint_t);
				ep->id = idx;
				ep->address =
						e2->Attribute("address") ?
								e2->Attribute("address") : "";
				ep->name = e2->Attribute("name");
				ep->host = e2->Attribute("host");
				ep->port = boost::lexical_cast<int>(e2->Attribute("port"));
				ep->type = RpcConnection::UNDEFINED;
				attr = e2->Attribute("type");
				boost::trim(attr);
				if (attr == "socket") {
					ep->type = RpcConnection::SOCKET;
				} else if (attr == "mq") {
					ep->type = RpcConnection::MQ;
				} else if (attr == "user") {
					ep->type = RpcConnection::USER;
				} else if (attr == "auto") {
					ep->type = RpcConnection::AUTO;
				} else if( attr == "websocket"){
					ep->type = RpcConnection::WEBSOCKET;
				} else {
					log_error(LOGTCE, "unrecognized mq type:%s", %attr)
					return false;
				}
				eps[ep->name] = ep;

				idx++;
				e2 = e2->NextSiblingElement("ep");
			}
		} else if (tag == "servers") {
			e2 = e->FirstChildElement("server");
			while (e2) {
				attr = e2->Attribute("name");
				if (attr != svcname) {
					e2 = e2->NextSiblingElement("server");
					continue;
				}
				ServerDetailPtr server(new ServerDeatil_t);
				server->name = attr;
				attr = e2->Attribute("id");
				server->id = boost::lexical_cast<uint16_t>(attr);
				attr = e2->Attribute("type");

				if (name_svcdefs.find(attr) == name_svcdefs.end()) {
					log_error(LOGTCE, "Service < %s > undefined!", %attr);
					return false;
				}
				server->service = name_svcdefs[attr];

				std::vector<RouteDetailPtr> routes;
				e3 = e2->FirstChildElement();
				while (e3) {
					tag = e3->Value() ? e3->Value() : "";
					if (tag == "route") {
						attr = e3->Attribute("if");
						log_debug(LOGTCE, "server: %s, if:%s",
								%server->name%attr);

						if (name_ifdefs.find(attr) == name_ifdefs.end()) {
							log_error(LOGTCE,
									"route error, if:< %s > not found!", %attr);
							return false;
						}
						RouteDetailPtr route(new RouteDetail_t);
						route->ifx = name_ifdefs[attr];

						//TiXmlElement* c,*r;
						std::vector<std::string> ins, outs;
						e4 = e3->FirstChildElement();
						while (e4) {
							RouteInOutPairPtr inout;
							std::string type = e4->Value();
							log_debug(LOGTCE, "route :%s", %type);
							if (type == "call" || type == "return") {
								inout = RouteInOutPairPtr(new RouteInOutPair_t);
								attr = e4->Attribute("in");
								boost::trim(attr);
//									if( attr!="*"){
								if (eps.find(attr) == eps.end()) {
									log_error(LOGTCE,
											"endpoint < %s > not found!",
											%attr);
									return false;
								}
								inout->in = eps[attr];
								server->name_eps[attr] = eps[attr];
								server->mq_reads[attr] = eps[attr];
								eps[attr]->access|= AF_READ;
//									}

								attr = e4->Attribute("out");
								boost::trim(attr);
//									if(attr!="*"){
								if (eps.find(attr) == eps.end()) {
									log_error(LOGTCE,
											"endpoint < %s > not found!",
											%attr);
									return false;
								}
								inout->out = eps[attr];
								server->name_eps[attr] = eps[attr];
								server->mq_writes[attr] = eps[attr];
								eps[attr]->access|= AF_WRITE;
//									}
								if (type == "call") {
									route->calls[inout->in->id] = inout; //
								} else {
									route->returns[inout->in->id] = inout;
								}
							}
							e4 = e4->NextSiblingElement();
						}
						server->routes[route->ifx->ifidx] = route;
					} //if( e3->Value() == "route")
					else if (tag == "extra_mqs") {
						std::string ins, outs;
						ins = e3->Attribute("ins");
						outs = e3->Attribute("outs");
						std::vector<std::string> items;

						boost::split(items, ins, boost::is_any_of(","),
								boost::token_compress_on);
						BOOST_FOREACH(std::string name,items){
						boost::trim(name);
						if( name == "") continue;
						if( eps.find(name) == eps.end()) {
							log_error(LOGTCE,"endpoint < %s > not found!",%name);
							return false;
						}
						server->mq_reads[name] = eps[name];
						server->name_eps[name] = eps[name];
						eps[name]->access |= AF_READ;
						}

						boost::split(items, outs, boost::is_any_of(","),
								boost::token_compress_on);
						BOOST_FOREACH(std::string name,items){
						boost::trim(name);
						if( name == "") continue;
						if( eps.find(name) == eps.end()) {
							log_error(LOGTCE,"endpoint < %s > not found!",%name);
							return false;
						}
						server->mq_writes[name] = eps[name];
						server->name_eps[name] = eps[name];
						eps[name]->access |= AF_WRITE;
						}
					}else if( tag =="properties"){
						e4 = e3->FirstChildElement("property");
						std::string name,value;
						while(e4){
							name = e4->Attribute("name")?e4->Attribute("name"):"";
							if(name == ""){
								e4 = e4->NextSiblingElement("property");
								continue;
							}
							value = e4->Attribute("value")?e4->Attribute("value"):"";
							server->props[name] = value;
							e4 = e4->NextSiblingElement("property");
						}
					}
					e3 = e3->NextSiblingElement();
				} // end route

				_localserver = server;
				e2 = e2->NextSiblingElement("server");
			}
		}
//		else if( tag == "LocalServer"){
//			localname = e->Attribute("name");
//		}
		e = e->NextSiblingElement();
	}

	_id_svcdefs = id_svcdefs;
	_name_svcdefs = name_svcdefs;
	///////////////////////////////////////////////////////
	// 服务消息配置信息已经读取完毕
	if (_localserver.get() == 0) {
		log_error(LOGTCE, "LocalServer not defined!");
		return false;
	}
	uint16_t serverid;
	serverid = (_localserver->id & 0xff) | (_localserver->service->id << 8);
	_localserver->id = serverid;
	RpcCommunicator::instance().localServiceId() = serverid;

	///////////////////////////////////////////////////////
	return run();
}

bool MqSet::run() {
	//
//	std::map<IF_IDX, RouteDetailPtr >::iterator itr;
	std::map<std::string, RpcRouteEndPointPtr>::iterator itr;
	;
	for(itr = _localserver->name_eps.begin();itr!=_localserver->name_eps.end();itr++){
		RpcRouteEndPointPtr ep = itr->second;

		if (ep->type == RpcConnection::SOCKET) {
			ep->impl = IEndPointImplPtr(new SocketAdapter_impl);
		} else if (ep->type == RpcConnection::MQ) {
#ifdef _QPID
			ep->impl = IEndPointImplPtr(new MQ_impl);
#endif
		}else if (ep->type == RpcConnection::WEBSOCKET){
#ifdef _WEBSOCKET
			ep->impl = IEndPointImplPtr(new WebSocketAdapter_impl);
#endif
		} else if (ep->type == RpcConnection::USER
				|| ep->type == RpcConnection::AUTO) {
			ep->impl = IEndPointImplPtr(new UnRealize_impl);
		}
		if (!ep->impl->open(ep)) {
			log_error(LOGTCE, "open endpoint < %s >  failed!",
					%ep->name);
			return false;
		}
	}
	RpcCommunicator::instance().appendObserver( shared_from_this() );

	/*
	for (itr = _localserver->mq_reads.begin();
			itr != _localserver->mq_reads.end(); itr++) {
		RpcRouteEndPointPtr ep = itr->second;

		if (ep->type == RpcConnection::SOCKET) {
			if (ep->impl.get() == NULL) {
				ep->impl = IEndPointImplPtr(new SocketAdapter_impl);
			}
		} else if (ep->type == RpcConnection::MQ) {
			ep->impl = IEndPointImplPtr(new MQ_impl);
		} else if (ep->type == RpcConnection::USER
				|| ep->type == RpcConnection::AUTO) {
			ep->impl = IEndPointImplPtr(new UnRealize_impl);
		}
		if (!ep->impl->open(ep, AF_READ)) {
			log_error(LOGTCE, "open endpoint < %s > for reading failed!",
					%ep->name);
			return false;
		}
	}

	for (itr = _localserver->mq_writes.begin();
			itr != _localserver->mq_writes.end(); itr++) {
		RpcRouteEndPointPtr ep = itr->second;
		if (ep->type == RpcConnection::SOCKET) {
			if (ep->impl.get() == NULL) {
				ep->impl = IEndPointImplPtr(new SocketAdapter_impl);
			}
		} else if (ep->type == RpcConnection::MQ) {
			ep->impl = IEndPointImplPtr(new MQ_impl);
		} else if (ep->type == RpcConnection::USER) {
			ep->impl = IEndPointImplPtr(new UnRealize_impl);
		} else if (ep->type == RpcConnection::AUTO) { //
			ep->impl = IEndPointImplPtr(new AutoBack_impl);
		}
		if (!ep->impl->open(ep, AF_WRITE)) {
			log_error(LOGTCE, "open endpoint < %s > for writing failed!",
					%ep->name);
			return false;
		}
	}
	*/
	return true;
}

////设置下一站路由队列方向
//void MqSet::routeMessage(const std::string & mq,RpcContext* ctx){
//
//}
//
//int MqSet::onMessageGet_Socket(RpcMessagePtr& msg){
//	if( isLocalMessage(msg)){
//		return MSG_IGNORED; //放行，让app层接收
//	}
//	postMessage(msg);
//	return MSG_CONSUMED;
//}
//
//int MqSet::onMessageGet_Mq(RpcMessagePtr& msg){
//	QMssageAttribute_t* attr = (QMssageAttribute_t*) msg->delta.get();
//	return MSG_IGNORED;
//}
//
//
//std::string MqSet::getRouteMqFromToken( const RpcMessagePtr& msg){
//	return "";
//}
//
////是否从socket上过来,反之从mq上过来
//bool isFromSocket(RouteDetailPtr route,RpcMessagePtr& msg){
//
//	return false;
//}

/**
 * 判断是否本地消息有两种情况
 * 1.调用本地Rpc请求的Call消息进入
 * 2.由本地服务发起的向外的Rpc请求的return消息，依靠Message::call_id识别
 */

bool MqSet::isLocalMessage(const RpcMessagePtr& m) {

	if ((m->calltype & RpcMessage::RETURN)
			&& (m->call_id == RpcCommunicator::instance().localServiceId())) {
		return true;
	}
	//调用本地接口，判别接口是否存在(必须在xml中配置)
	if (m->calltype & RpcMessage::CALL) {
		if (_localserver->service->if_exist(m->ifidx)) {
			return true;
		}
	}
	return false;
}

///截获token必须在Mqet之前设置observer
///截获接收的数据
int MqSet::onMessageGet(RpcMessagePtr& msg) {
	if (isLocalMessage(msg)) {
		return MSG_IGNORED; //放行
	}
	if ((msg->calltype & RpcMessage::CALL)
			&& msg->call_id == RpcCommunicator::instance().localServiceId()) {
		//skipp 自己发给自己的消息 直接忽略
		return MSG_DROPPED;
	}
	std::map<IF_IDX, RouteDetailPtr>::iterator itr1;
	itr1 = _localserver->routes.find(msg->ifidx);
	if (itr1 == _localserver->routes.end()) {
		return MSG_DROPPED; //未进行配置路由，消息丢弃
	}
	std::vector<RouteDetailPtr>::iterator itrRoutes;
	EP_IDX epidx = msg->conn->ep_idx();
	RouteInOutPairPtr inoutpair;
	inoutpair = _localserver->findOutRouteInOutPair(msg->ifidx, msg->calltype,
			epidx);
	if (inoutpair.get() == NULL) {
		return MSG_DROPPED;
	}
	//已从路由表中找到目的endpoints
	if (inoutpair->out.get()) {
		inoutpair->out->impl->sendMessage(msg);
	}
	return MSG_CONSUMED;
}

///截获即将发送的数据
///消息来自 Communicator::sendMessage()
int MqSet::onMessagePut(RpcMessagePtr& msg) {
	//本地服务CALL之后返回的RETURN包
//	if ((msg->calltype & RpcMessage::RETURN)
//			&& _localserver->service->if_exist(msg->ifidx)) {
	if (msg->calltype & RpcMessage::RETURN){
		if (msg->callmsg.get() == NULL) {
			log_error(LOGTCE,
					"callmsg is null, please check tce2cpp.py if correct!");
			return MSG_DROPPED;
		}
		if(msg->callmsg->conn->getType() == RpcConnection::SOCKET ||
				msg->callmsg->conn->getType() == RpcConnection::WEBSOCKET){
			return MSG_IGNORED; // socket连接上额call，并在原有连接上返回
		}
		RouteInOutPairPtr inout = _localserver->findOutRouteInOutPair(
				msg->callmsg->ifidx, msg->callmsg->calltype,
				msg->conn->ep_idx());
		std::vector<RpcRouteEndPointPtr>::iterator itr;

		if (inout.get()) {
			inout->out->impl->sendMessage(msg);
		}
		return MSG_CONSUMED;
	}
	return MSG_IGNORED;
}

RpcRouteEndPointPtr MqSet::getRouteEndpointWithMqAttr(uint16_t src_type,
		uint16_t src_id) {
	if (_id_svcdefs.find(src_type) == _id_svcdefs.end()) {
		return RpcRouteEndPointPtr();
	}
	ServicePtr svc = _id_svcdefs[src_type];
	boost::format fmt(svc->mq_pattern);
	try {
		fmt % src_id;
		fmt.str();
		return _localserver->findOutEnpoint(fmt.str()); //找到发送mq名称对应的mq链接
	} catch (std::exception & e) {
		log_error(LOGTCE, "invalid mq_pattern of service < %s > : %s",
				%svc->name%svc->mq_pattern);
	}
	return RpcRouteEndPointPtr();
}

////////////////////////////////////////////////////////////
//} // end mqroute

}// end TCE

