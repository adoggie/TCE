
#include "plainconfig.h"
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <algorithm>

/*
#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/utility.hpp>
#include <boost/format.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
*/
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>

namespace tce{

PlainConfig::~PlainConfig(){

}

PlainConfig::PlainConfig(){

}

PlainConfig::PlainConfig(const Properties_t& props){
	_props = props;
}

PlainConfig::PlainConfig(const std::string & file){
	load(file);
}

bool PlainConfig::load(const std::string & file){
	boost::filesystem::path path(file);
	size_t size = 0;
	std::ifstream ifile;

	try{size = boost::filesystem::file_size(path);}catch(...){return false;}


	FILE * fp = fopen(file.c_str(),"r");
	std::vector<char> buf(size+1);
	buf[size] = '\0';
	fread(&buf[0],size,1,fp);
	fclose(fp);

	std::vector<std::string> lines;
	boost::split( lines,buf,boost::is_any_of("\n"),boost::token_compress_on);
	BOOST_FOREACH(std::string text,lines){

		boost::trim(text);
		//std::cout<<text<<std::endl;
		if(text.size()==0 ||  text[0] == '#'){
			continue;
		}
		//std::cout<<text<<std::endl;
		std::vector<std::string> params;
		boost::split( params,text,boost::is_any_of("#"),boost::token_compress_on);
		if(params.size()){
			text = params[0];
		}
		boost::split( params,text,boost::is_any_of("="),boost::token_compress_on);
		if(params.size()<2){
			continue;
		}
		std::vector<std::string> params2;
		params2.insert( params2.end(),params.begin()+1,params.end());
		std::string key,value;
		key = params[0];
		boost::trim(key);
		//BOOST_FOREACH(std::string& p,params2){
			; //boost::trim(p);
		//}
		value = boost::algorithm::join(params2,"=");
		boost::trim(value);
		//
		_props[key] = boost::any(value);
		//std::cout<<key<<":"<<value<<std::endl;
	}

	return true;
}

boost::any PlainConfig::getProperty(const std::string& name){
	if( _props.find(name) == _props.end()){
		return boost::any();
	}
	return _props[name];
}




void PlainConfig::reset(){

}





}
