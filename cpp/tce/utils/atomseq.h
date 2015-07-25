
#ifndef _UTILS_ATOMSEQ_H
#define _UTILS_ATOMSEQ_H

#include <boost/thread/mutex.hpp>
#include <limits>

namespace tce{

namespace utils{

class AtomSequenceInt{
	unsigned int _initseq;
	unsigned int _step;
	unsigned int _current;
	unsigned int _max;
	bool	_cycled ;
	boost::mutex _mtx;
public:

	AtomSequenceInt(unsigned int initseq = 0,unsigned int step=1){
		_initseq = initseq;
		_step = step;
		_cycled = true;
		_current = _initseq;
		_max = std::numeric_limits<unsigned int>::max();
	}

	void reset(){
		boost::mutex::scoped_lock(_mtx);
		_current = _initseq;
	}

	unsigned int nextval(){
		boost::mutex::scoped_lock(_mtx);
		return ++_current;
	}


};

} // namespace utils

}

#endif

