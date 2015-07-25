
#ifndef _TCE_UTILS_H
#define _TCE_UTILS_H

#include "base.h"
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/lexical_cast.hpp>

namespace tce{

namespace utils{

	//template <typename T>
	inline std::string getPropertyValue(const Properties_t props,const std::string& name,const std::string& default_=""){
		std::string value;
		Properties_t::const_iterator itr;
		itr = props.find(name);
		if(itr == props.end()){
			return default_;
		}
		try{
			value = boost::lexical_cast<std::string>(itr->second);
		}catch(...){
			value = default_;
		}
		return value;
	}

}

}

#endif

