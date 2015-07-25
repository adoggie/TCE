
#ifndef _TCE_LOGBASE_H
#define _TCE_LOGBASE_H

#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <list>
#include <deque>

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/format.hpp>

namespace tce{
class Logger;
typedef boost::shared_ptr<Logger> LoggerPtr;

class Logger{
public:
	Logger(){

	}

	~Logger(){
		//flush();
	}
	static LoggerPtr create(){
		return LoggerPtr(new Logger);
	}

	enum Types{
		FATAL,
		ALERT,
		CRIT,
		ERROR,
		WARN,
		INFO,
		DEBUG,

	};
	class Handler{
	public:
		virtual ~Handler(){};
		virtual void write(const std::string& log,Types type =INFO )=0;
		virtual void flush()=0; //异步写入
	};
	typedef boost::shared_ptr<Handler> HandlerPtr;

	void addHandler(HandlerPtr h){
		_handlers.push_back(h);
	}

	//需要外部驱动执行
	void flush(){
		std::vector<HandlerPtr>::iterator itr;
		for(itr=_handlers.begin();itr!=_handlers.end();itr++){
			(*itr)->flush();
		}
	}

	void write(const std::string& log,Types type){
		std::vector<HandlerPtr>::iterator itr;
		for(itr=_handlers.begin();itr!=_handlers.end();itr++){
			(*itr)->write(log,type);
		}
	}
private:
	std::vector<HandlerPtr> _handlers;
	boost::mutex _mtx;
};




}


#define log_log(logger,FMT,LEVEL,args...)  	{ \
							std::string sfmt = FMT + std::string("%s");\
							boost::format fmt(sfmt );\
							fmt args  %"";\
							logger->write(fmt.str(),LEVEL);\
							}
#define log_debug(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::DEBUG,args)
#define log_info(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::INFO,args)
#define log_warn(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::WARN,args)
#define log_error(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::ERROR,args)


#endif


