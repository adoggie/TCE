package tce.utils;

public class GrammarXML {

	//从类型名称获取XML数据中的Tag
	//tc_redirect_p_User_t 末尾的User,作为 <User>
	public static String extractXMLTag(String typeName){
		return "";
	}
}


/*


interface Terminal{


};


struct tc_redirect_p_User_t{
	string token; 
};

struct tc_redirect_r_Result_t{
	int 	code;
	string 	tc_srv_ip;
	int 	tc_srv_port;
	string msg;
};


struct tc_redirect_p_t{
	tc_redirect_p_User_t User;
};

struct tc_redirect_r_t{
	tc_redirect_r_Result_t Result;
};


interface TC{
	tc_redirect_r_t redirect( tc_redirect_p_t p);	
};



struct ts_heartbeat_p_User_t{
	string id;
};


struct ts_heartbeat_p_t{
	ts_heartbeat_p_User_t User;
};



struct ts_gps_p_GPS_t{
	float lon;
	float lat;
	float speed;
	float angle;
	int		time;
};

struct ts_gps_p_t{
	ts_gps_p_GPS_t gps;
};




struct ts_verify_r_User_t{
	string id;
};

struct ts_verify_r_Group_t{
	string id;
	string name;
	string type;
};

sequence<ts_verify_r_Group_t> ts_verify_r_Groups_t;

struct ts_verify_r_Result_t{
	int code;
	ts_verify_r_User_t user;
	ts_verify_r_Groups_t groups;
};

struct ts_verify_r_t{
	ts_verify_p_Result_t Result;
};


struct ts_verify_p_User_t{
	string token;
};

struct ts_verify_p_t{
	ts_verify_p_User_t user;
};

interface TS{
	void heartbeat(ts_heartbeat_p_t p);
	void gps(ts_gps_p_t p);
	ts_verify_p_Result_t verify(ts_verify_p_t p);
};





*/