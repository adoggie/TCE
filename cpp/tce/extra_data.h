
#ifndef _RPC_EXTRADATA_H
#define _RPC_EXTRADATA_H

#include "base.h"
#include "bytearray.h"
#include <boost/shared_ptr.hpp>


namespace tce{

//class RpcExtraData;
//typedef boost::shared_ptr<RpcExtraData> RpcExtraDataPtr;
class RpcExtraData{
public:
//	enum DataType_t{
//		NODATA = 0 , 	// 0 表示没有附加数据，每种数据都可以自己标识自己
//		BYTE_STREAM = 1,
//		STRING=2,
//		STRING_DICT= 3,
//		STRING_LIST = 4
//	};
//	#define EXTRA_DATA_TYPE(d) ((d>>24)&0xff)
//	#define EXTRA_DATA_SIZE(d)  ( d&0xffffff)
	
	bool unmarshall(ByteArray & d ){
		if( d.remain() < 4){
			return false;
		}
		uint32_t size;
		size = d.readUnsignedInt();

		try{
			for(size_t n = 0; n< size; n++){
				std::string k,v;
				k = d.readString();
				v = d.readString();
				_props[k] = v;
			}
		}catch(RpcException& e){
			return false;
		}
//		uint8_t type = EXTRA_DATA_TYPE(size);
//		size = EXTRA_DATA_SIZE(size);
//		if( type < NODATA || type > STRING_LIST ){
//			return false;
//		}
//		_type = (DataType_t)type;
//		if( d.remain() < (int) size){
//			return false; //数据不够
//		}
//		_data.reset();
//		_data.writeBytes2(d,d.position(),size);
		return true;
	}

	void marshall(ByteArray& d){
//		size_t size = datasize();
//		size = ( size&0xffffff) | ( (_type&0xff) << 24);
		d.writeUnsignedInt(_props.size());
		std::map<std::string,std::string>::iterator itr;
		for(itr=_props.begin();itr!=_props.end();itr++){
			d.writeString(itr->first);
			d.writeString(itr->second);
		}
	}
	
	//static RpcExtraDataPtr create();
//
//	DataType_t type(){
//		return _type;
//	}
	
	uint32_t size(){
		return datasize()+4;
	}
	
	uint32_t datasize(){
		size_t size = 0;
		std::map<std::string,std::string>::iterator itr;
		for(itr=_props.begin();itr!=_props.end();itr++){
			size+=itr->first.size() + itr->second.size() + 8;
		}
		return size;
	}
	
//	ByteArray getBytes(){
//		ByteArray r;
//		if( _type!= BYTE_STREAM || _data.size()){
//			return r;
//		}
//		r.writeBytes2(_data,)
//		return _data;
//	}

	std::map<std::string,std::string> getStrDict(){
		return _props;
//		uint32_t size;
//		std::map<std::string,std::string>  r;
//		if( _type != STRING_DICT){
//			return r;
//		}
//		try{
//			size = _data.readUnsignedInt();
//			for(size_t n = 0; n< size; n++){
//				std::string k,v;
//				k = _data.readString();
//				v = _data.readString();
//				r[k] = v;
//			}
//		}catch(RpcException& e){
//			return std::map<std::string,std::string>();
//		}
//		return r;
	}

//	std::string getStr(){
//		if( _type!= STRING){
//			return "";
//		}
//		std::string r;
//
//		try{
//			r = _data.readString();
//		}catch(RpcException& e){
//			return "";
//		}
//	}

//	std::vector<std::string> getStrList(){
//
//	}

	std::string getValue(const std::string name,const std::string& default_="" ){
//		if( _type != STRING_DICT){
//			return default_;
//		}
//		std::map<std::string,std::string> strdict;
//		strdict = getStrDict();
		if( _props.find(name) == _props.end()){
			return default_;
		}
		return _props[name];
	}
//
//	void set(const char * data,size_t size){
//		_type =BYTE_STREAM;
//		_data.reset();
//		_data.writeBytes3(data,size);
//	}

	void set(const std::map< std::string,std::string>& props){
		_props = props;
//		_type =STRING_DICT;
//		_data.reset();
//		std::map<std::string,std::string>::const_iterator itr;
//		size_t size;
//		size = strdict.size();
//		_data.writeUnsignedInt(size);
//		for(itr = strdict.begin();itr!=strdict.end();itr++){
//			_data.writeString(itr->first);
//			_data.writeString(itr->second);
//		}

	}

//	void set(std::vector<std::string>& strlist){
//		_type =STRING_LIST;
//		_data.reset();
//		std::vector<std::string>::iterator itr;
//		size_t size;
//		size = strlist.size();
//		_data.writeUnsignedInt(size);
//		for(itr = strlist.begin();itr!=strlist.end();itr++){
//			_data.writeString(*itr);
//		}
//
//	}
//	void set(const std::string& str){
//		_type = STRING;
//		_data.writeString(str);
//	}
	
	
	
public: 
	RpcExtraData(){
//		_type = NODATA ;
	}
private: 
//	DataType_t _type;
//	ByteArray _data;
	std::map<std::string,std::string> _props;
};


}


#endif

