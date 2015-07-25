
#ifdef _WEBSOCKET

#include "websocket_conn.h"
#include "websocket_adapter.h"
#include "../communicator.h"
#include "websocket_conn.h"
 #include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

#include <websocketpp.hpp>
//

//using websocketpp::server;

namespace tce{


bool WebSocketAdapter::open(const std::string& uri,const options_type& opts  ){
	RpcCommAdapter::open(uri,opts);

	_handler = websocketpp::server::handler::ptr(new websocket_handler(this));

	std::vector<std::string> params;
	boost::split( params,_uri,boost::is_any_of(": \t"),boost::token_compress_on);
	if(params.size()<2){
		return false;
	}

	try{

//		_endpoint->alog().set_level(websocketpp::log::alevel::CONNECT);
//		_endpoint->alog().set_level(websocketpp::log::alevel::DISCONNECT);
//
//		_endpoint->elog().set_level(websocketpp::log::elevel::RERROR);
//		_endpoint->elog().set_level(websocketpp::log::elevel::FATAL);

		_thread = boost::shared_ptr<boost::thread>( new boost::thread( boost::bind(&WebSocketAdapter::listenThread,this,params[1]) ) );
//		listenThread(params[1]);

	//_endpoint->listen( boost::lexical_cast<uint16_t>(params[1]));
	}catch(std::exception& e){
		log_error(LOGTCE,"websocket open failed! address:%s",%uri);
	}

	return true;
}

void WebSocketAdapter::close(){
	return RpcCommAdapter::close();
}

int WebSocketAdapter::onConnected(const RpcConnectionPtr& conn){
	return RpcCommAdapter::onConnected(conn);
}

void WebSocketAdapter::onDisconnected(const  RpcConnectionPtr& conn){
	return RpcCommAdapter::onDisconnected(conn);
}


WebSocketAdapter::WebSocketAdapter(){

}

WebSocketAdapter::~WebSocketAdapter(){

}



void WebSocketAdapter::websocket_handler::on_open(websocketpp::server::connection_ptr con){
	adapter->on_open(con);
}

void WebSocketAdapter::websocket_handler::on_close(websocketpp::server::connection_ptr con){
	adapter->on_close(con);
}

void WebSocketAdapter::websocket_handler::on_message(websocketpp::server::connection_ptr con,websocketpp::message::data_ptr msg){
	adapter->on_message(con,msg);
}


void WebSocketAdapter::on_open(websocketpp::server::connection_ptr con){
	std::cout<<"connected"<<std::endl;
	WebSocketConnectionPtr conn( new WebSocketConnection(con));
	addConnection( conn );
	conn->ep_idx() = ep_idx(); //
	conn->attachAdapter(shared_from_this());

	conn->onConnected();

	boost::unique_lock<boost::shared_mutex> write(_mtxconns);
	_connsmap[con] = conn;

}

void WebSocketAdapter::on_close(websocketpp::server::connection_ptr con){

	std::cout<<"lost"<<std::endl;
	boost::unique_lock<boost::shared_mutex> write(_mtxconns);
	std::map<websocketpp::server::connection_ptr,WebSocketConnectionPtr>::iterator itr;
	itr = _connsmap.find(con);


	if(itr == _connsmap.end()){
		return;
	}
	WebSocketConnectionPtr conn = itr->second;
	_connsmap.erase(itr);
	conn->onDisconnected(); // probleam is here, fuck!

	return ;
}

void WebSocketAdapter::on_message(websocketpp::server::connection_ptr con,websocketpp::message::data_ptr msg){


	std::map<websocketpp::server::connection_ptr,WebSocketConnectionPtr>::iterator itr =_connsmap.end() ;
	{
		boost::shared_lock<boost::shared_mutex> read(_mtxconns);
		itr = _connsmap.find(con);

	}
	if(itr == _connsmap.end()){
		return;
	}
	itr->second->onMessage(msg);
}

void WebSocketAdapter::salfCheck(){
	log_debug(LOGTCE,"websocketpp  interval-salfcheck()");
	_chktimer->expires_from_now(boost::posix_time::seconds(5));
	_chktimer->async_wait( boost::bind(&WebSocketAdapter::salfCheck,this));
}


static websocketpp::server::ptr _websocket_endpoint;
static uint16_t _websocket_listen_port = 0;;
void websocket_listen(){
	if(_websocket_endpoint.get()){
		try{
			_websocket_endpoint->listen( _websocket_listen_port);
		}catch(std::exception&e){
			for(;;)
					    {
					        try
					        {
					        	_websocket_endpoint->get_io_service().reset();
					        	_websocket_endpoint->get_io_service().run();
					            break;
					        }
					        catch( const std::exception & ex )
					        {
					        	log_error(LOGTCE,"websocket listen exception: %s",%e.what());
					        }
					    }
		}
	}
}

void WebSocketAdapter::listenThread(const std::string& port){
	try{
		//_websocket_listen_port = boost::lexical_cast<uint16_t>(port);
		_endpoint = websocketpp::server::ptr(new websocketpp::server(_handler));

		_endpoint->alog().set_level(websocketpp::log::alevel::CONNECT);
		_endpoint->alog().set_level(websocketpp::log::alevel::DISCONNECT);
		_endpoint->elog().set_level(websocketpp::log::elevel::RERROR);
		_endpoint->elog().set_level(websocketpp::log::elevel::FATAL);

		//_chktimer = boost::shared_ptr<boost::asio::deadline_timer>(new boost::asio::deadline_timer(_endpoint->get_io_service(),boost::posix_time::seconds(5))) ;
		//_chktimer->async_wait( boost::bind(&WebSocketAdapter::salfCheck,this));
		_endpoint->listen( boost::lexical_cast<uint16_t>(port));



	}catch(std::exception& e){

		log_error(LOGTCE,"websocket listen exception: %s",%e.what());
		for(;;)
		    {
		        try
		        {
		        	_endpoint->get_io_service().reset();
		        	_endpoint->get_io_service().run();
		            break;
		        }
		        catch( const std::exception & ex )
		        {
		        	log_error(LOGTCE,"websocket listen exception: %s",%e.what());
		        }
		    }
	}
}


}

#endif

