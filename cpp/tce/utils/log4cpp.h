
#ifndef _TCE_LOG4CPP_H
#define _TCE_LOG4CPP_H

#include "logger.h"

#include <log4cpp/Category.hh>
#include <log4cpp/PropertyConfigurator.hh>

namespace tce{

class Log4cpp;
typedef boost::shared_ptr<Log4cpp> Log4cppPtr;

class Log4cpp:public Logger::Handler{
public:
	void write(const std::string& log,Logger::Types type = Logger::INFO );
	void flush();
	Log4cpp();
	~Log4cpp();


	static Log4cppPtr create(const std::string& logfile,const std::string& cat); // 日志配置文件
private:
	log4cpp::Category* _logcat;
};

inline
void Log4cpp::write(const std::string& log,Logger::Types type){
	switch( type){
	case Logger::DEBUG:
		_logcat->debug(log); break;
	case Logger::INFO:
		_logcat->info(log) ; break;
	case Logger::WARN:
		_logcat->warn(log) ; break;
	case Logger::ERROR:
		_logcat->error(log) ; break;
	case Logger::ALERT:
		_logcat->alert(log); break;
	case Logger::FATAL:
		_logcat->fatal(log); break;
	case Logger::CRIT: break;

	}

}

inline
void Log4cpp::flush(){

}

inline
Log4cpp::Log4cpp(){
	_logcat = NULL;
}

inline
Log4cpp::~Log4cpp(){

}

inline
Log4cppPtr Log4cpp::create(const std::string& logfile,const std::string& cat){
	Log4cppPtr log;
	try{
		log4cpp::PropertyConfigurator::configure( logfile);
		log = Log4cppPtr(new Log4cpp);
		log->_logcat = & log4cpp::Category::getInstance(cat);
	}catch(std::exception & e){
		std::cout<<e.what()<<std::endl;
		std::cout<<"load log4cpp config file failed! >>"<< logfile << std::endl;
	}

	return log;
}


}


#endif

