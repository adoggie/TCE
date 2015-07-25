
#ifndef _TCE_SINGLETON_H
#define _TCE_SINGLETON_H

#include "../base.h"

namespace tce{


template <typename T>
struct Singleton:public T{
	static boost::shared_ptr<T>& instance(){
		static boost::shared_ptr<T> _handle;
		if( !_handle.get()){
			_handle = boost::shared_ptr<T>(new T);
		}
		return _handle;
	}

	static T& instance2(){
		return *instance();
	}

};

}

#endif
