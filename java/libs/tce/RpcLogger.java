package tce;
import java.util.*;
public class RpcLogger {

	public static final int UNSET =0 ;
	public static final int DEBUG =1 ;
	public static final int INFO = 2;
	public static final int ERROR = 3;
	public static final int ALL = 5;

	private int _loglevel = ALL;

	public RpcLogger(){

	}

	public void setLevel(int level){
		_loglevel = level;
	}

	public void debug(String msg){
		if(_loglevel >= DEBUG) return;
		print(msg,DEBUG);
	}

	public void info(String msg){
		if(_loglevel >= INFO) return;
		print(msg,INFO);
	}

	public void error(String msg){
		if(_loglevel >= ERROR) return;
		print(msg,ERROR);
	}

	void print(String msg ,int level){
		String type = "";
		if(level == DEBUG) type = "DEBUG";
		if(level == INFO ) type = "INFO";
		if(level == ERROR) type = "ERROR";

		String timestr = Calendar.getInstance().getTime().toString();
		System.out.println(String.format("%s [ %s ] %s",timestr, type,msg));
	}
}
