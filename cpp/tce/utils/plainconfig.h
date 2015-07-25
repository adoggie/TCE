
#ifndef _TCE_PLAINCONFIG_H
#define _TCE_PLAINCONFIG_H

#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <list>
#include <deque>
#include <boost/any.hpp>

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <algorithm>

#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/lexical_cast.hpp>


namespace tce{

class PlainConfig{
public:

	typedef std::map<std::string,boost::any> Properties_t;
	typedef std::vector<std::string> StringList_t;

	//typedef std::vector<boost::any> Properties_t;

	~PlainConfig();
	PlainConfig();

	PlainConfig(const Properties_t& props);
	PlainConfig(const std::string & file);
	bool load(const std::string & file);

	template <typename T>
	void setProperty(const std::string & name,const T& value);
	boost::any getProperty(const std::string& name);

	template <typename T>
	T getProperty(const std::string& name,T default_);

	template <typename T>
	std::vector<T> getPropertyTuples(const std::string&name,const char * delimits);
protected:
	void reset();
private:
	Properties_t 	_props;

};

template  < typename T>
inline std::vector<T> PlainConfig::getPropertyTuples(const std::string&name,const char * delimits=","){
	boost::any val ;
	std::vector<T> r;
	val = getProperty(name);
	if( val.empty()){
		return r;
	}

	std::vector<std::string>params;
	std::string line = boost::any_cast<std::string>(val);
	boost::split( params,line,boost::is_any_of(delimits),boost::token_compress_on);

	BOOST_FOREACH(std::string s,params){
		boost::trim(s);
		T it;
		try{
			//it = boost::any_cast<T>( boost::any(s));
			it = boost::lexical_cast<T>(s);
		}catch(...){
			//std::cout<< e.what() <<std::endl;
			continue;
		}
		r.push_back(it);
	}
	return r;
}



template <typename T>
inline T PlainConfig::getProperty(const std::string& name,const T default_){
	boost::any v = getProperty(name);
	if(v.empty() == false){
		try{
			T r = boost::lexical_cast<T>( boost::any_cast<std::string>(v) );
			return r;
		}catch(...){}
	}
	return default_;
}




template <typename T>
inline void PlainConfig::setProperty(const std::string & name,const T& value){
	_props[name] =value;
}



}

#endif
