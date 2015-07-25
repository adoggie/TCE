
#ifndef _TCE_Log4cxx_H
#define _TCE_Log4cxx_H

#include "logger.h"

#include <log4cxx/logger.h>
#include <log4cxx/logstring.h>
#include <log4cxx/propertyconfigurator.h>

namespace tce{

class Log4cxx;
typedef boost::shared_ptr<Log4cxx> Log4cxxPtr;

class Log4cxx:public Logger::Handler{
public:
	void write(const std::string& log,Logger::Types type = Logger::INFO );
	void flush();
	Log4cxx();
	~Log4cxx();


	static Log4cxxPtr create(const std::string& logfile,const std::string& cat); // 日志配置文件
private:
	//Log4cxx::Category* _logcat;
	log4cxx::LoggerPtr _log;
};

inline
void Log4cxx::write(const std::string& log,Logger::Types type){
	switch( type){
	case Logger::DEBUG:
		//_logcat->debug(log);
		LOG4CXX_DEBUG(_log,log);
		break;
	case Logger::INFO:
		//_logcat->info(log) ;
		LOG4CXX_INFO(_log,log);
		break;
	case Logger::WARN:
		//_logcat->warn(log) ;
		LOG4CXX_WARN(_log,log);
		break;
	case Logger::ERROR:
		//_logcat->error(log) ;
		LOG4CXX_ERROR(_log,log);
		break;
	case Logger::ALERT:
		//_logcat->alert(log);
		LOG4CXX_WARN(_log,log);
		break;
	case Logger::FATAL:
		//_logcat->fatal(log);
		LOG4CXX_FATAL(_log,log);
		break;
	case Logger::CRIT:
		break;

	}

}

inline
void Log4cxx::flush(){

}

inline
Log4cxx::Log4cxx(){
	//_logcat = NULL;
}

inline
Log4cxx::~Log4cxx(){

}

inline
Log4cxxPtr Log4cxx::create(const std::string& logfile,const std::string& cat){
	Log4cxxPtr log;
	try{
		log4cxx::PropertyConfigurator::configure(logfile);

		//_log = log4cxx::Logger::getLogger(cat);
		//Log4cxx::PropertyConfigurator::configure( logfile);
		log = Log4cxxPtr(new Log4cxx);
		log->_log = log4cxx::Logger::getLogger(cat);

	}catch(std::exception & e){
		std::cout<<e.what()<<std::endl;
		std::cout<<"load Log4cxx config file failed! >>"<< logfile << std::endl;
	}

	return log;
}


}


#endif

