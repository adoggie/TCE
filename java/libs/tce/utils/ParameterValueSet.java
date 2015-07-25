package tce.utils;

import java.util.HashMap;

/**
 * Created by scott on 7/11/15.
 */


public class ParameterValueSet{
	HashMap<String,String> _props = new HashMap<String, String>();

	public ParameterValueSet(){

	}

	public ParameterValueSet addParameter(String name,String value){
		_props.put(name,value);
		return this;
	}

	public HashMap<String,String> data(){
		return _props;
	}
}