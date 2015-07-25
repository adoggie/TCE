
#ifndef _UTILS_MUTEXOBJ_H
#define _UTILS_MUTEXOBJ_H

#include <boost/smart_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/condition_variable.hpp>

#include <limits>

namespace tce{

template <typename T>

class MutexObject{
	boost::shared_ptr<T> _d;

	boost::mutex _mtx;
	boost::condition_variable _cond;
public:
	boost::shared_ptr<T> waitObject(int timeout){ // ms
		boost::shared_ptr<T> d;
		boost::mutex::scoped_lock lock(_mtx);
		if( _d.get()){
			d = _d;
		}else{
			//boost::posix_time::seconds;
			if(!timeout){
				_cond.wait(lock);
			}else{
				_cond.timed_wait(lock,boost::get_system_time() + boost::posix_time::milliseconds(timeout));
			}
			d = _d;
		}
		return d;
	}

	void notify( const boost::shared_ptr<T>& d){
		{
			boost::mutex::scoped_lock lock(_mtx);
			_d =d;
		}

		_cond.notify_one();
	}


};

}

#endif

