package tce.mq;

import com.sun.swing.internal.plaf.basic.resources.basic_ko;
//import easymq.message_t;
/**
 *
 * http://qpid.apache.org/releases/qpid-0.28/index.html
 *
 * shit ! qpidd 启动必须关闭 auth
 *
 *  ./qpidd --pid-dir=/var/run --auth no --data-dir=$DATA_DIR --daemon
 */
import java.io.File;
import java.util.*;
import javax.jms.*;

import org.ho.yaml.Yaml;
import org.apache.qpid.client.AMQAnyDestination;
import org.apache.qpid.client.AMQConnection;
import tce.*;


public class RpcConnection_QpidMQ extends RpcConnection {
	public final static  int QUEUE = 0;
	public final static  int TOPIC = 1;
	public final static  int READ = 0x01;
	public final static  int WRITE = 0x02;
	public final static  int READWRITE = READ|WRITE;
	
	static HashMap<String,RpcConnection_QpidMQ> _mq_conns = new HashMap<String,RpcConnection_QpidMQ>();

//	private Vector<Thread>  _threads = new Vector<Thread>();
//	private Vector<message_t> _mq_msgs = new Vector<message_t>();
//	private BackWorker _worker = null;
//	private int _maxThreadNum = 1 ;
	
	private RpcConnection_QpidMQ _buddy = null;
	private int _readwrite;
	private boolean _exit = false;
	private RpcCommAdapter _adapter;
	private String _broker ;
	private String _address;
	private String _name;
	private Thread _threadRecv; //接收线程
	private Connection _conn= null;
	private Session _ssn = null;
	private MessageConsumer _msgConsumer = null;
	private MessageProducer _msgProducer = null;

	private RpcConnection_QpidMQ(String name,String broker,String address,int readwrite){
		super("",0);
		_name = name;
		_broker = broker;
		_address = address;
		_readwrite = readwrite;
	}


	/***
	 *
	 * @param name  必须是 mq名称
	 * @param broker
	 * @param address
	 * @param readwrite
	 * @return
	 */
	public static RpcConnection_QpidMQ create(String name,String broker,String address,int readwrite){
		RpcConnection_QpidMQ conn;
		conn = new RpcConnection_QpidMQ( name,broker,address, readwrite);

		if( !conn.connect() ){
			return null;
		}
		synchronized(_mq_conns){
			if(!_mq_conns.containsKey(name)){
				_mq_conns.put(name, conn);
			}
		}
		return conn;
	}

	public static RpcConnection_QpidMQ create(RpcEndPoint ep,int af_mode){
		return create(ep.name,ep.host,ep.address,af_mode);
	}

	public static RpcConnection_QpidMQ getConnection(String name){
		return _mq_conns.get(name);
	}

	String getUnique(){
		return _name;
	}
	
//	public static void setLoopbackMQ(RpcConnection_QpidMQ read,RpcConnection_QpidMQ write){
//		write._buddy = read;
//	}

	public void setLoopbackMQ(RpcConnection_QpidMQ recv_conn){

		_buddy = recv_conn;

	}
	
	@Override
	public void join(){
		try{
			_threadRecv.join();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}
	}
	
	@Override
	public boolean connect() {
		try{
			_conn= new AMQConnection(this._broker);
			_conn.start();
			_ssn = _conn.createSession(false,Session.AUTO_ACKNOWLEDGE);
			Destination dest = new AMQAnyDestination(_address);
			if( (_readwrite&RpcConnection_QpidMQ.READ) !=0){
				_msgConsumer = _ssn.createConsumer(dest);
				_threadRecv = new Thread(this);
				_threadRecv.start();
			}
			if( (_readwrite&RpcConnection_QpidMQ.WRITE)!=0){
				_msgProducer = _ssn.createProducer(dest);
			}
		}catch (Exception e){
			e.printStackTrace();
			return false;
		}
		return true;

	}

	
	@Override
	public void close(){
		_exit = true;
//		_worker.exit();
	}
	
	@Override
	protected
	synchronized boolean sendDetail(RpcMessage m){
		if( (m.calltype & RpcMessage.RETURN) !=0 ){ //回送消息
			String mqname = m.callmsg.extra.getPropertyValue("__mq_return__");
			if(mqname == null){
				return false;
			}
			if(_readwrite == RpcConnection_QpidMQ.READ){ //通过读的连接对象回送Rpc消息
				synchronized(_mq_conns){
					if(_mq_conns.containsKey(mqname)){
						RpcConnection_QpidMQ conn = _mq_conns.get(mqname);
						return conn.sendDetail(m); // it will reach next block
					}else{
						System.out.println("mq: "+ mqname + " not found,maybe you forgot initializing connection on start.");
					}
				}	
			}
			if(_readwrite == RpcConnection_QpidMQ.WRITE){
				try{
					BytesMessage msg = _ssn.createBytesMessage();
					msg.writeBytes(m.marshall());
					_msgProducer.send(msg);
				}catch (Exception e){
					e.printStackTrace();
					return false;
				}
				return true;
			}
		}
		
		if( (m.calltype & RpcMessage.CALL)!=0){
			//必须是接收MQ
			if( (_readwrite&WRITE) == 0){
				return false;
			}
			//非单向Rpc请求消息必须定义一个接收MQ以便接收RETURN消息包
			if( (m.calltype & RpcMessage.ONEWAY) == 0 && this._buddy == null){ //单向消息包
				System.out.println("read-mq have not defined!");
				return false;
			}
			if( (m.calltype & RpcMessage.ONEWAY) == 0){
				String name = _buddy.getUnique();
				m.extra.getProperties().put("__mq_return__", name); //设置接收消息队列
			}
			//-- 直接写消息到写队列
			try{
				BytesMessage msg = _ssn.createBytesMessage();
				msg.writeBytes(m.marshall());
				_msgProducer.send(msg);
			}catch (Exception e){
				e.printStackTrace();
				return false;
			}
			return true;
		}
		return false;
	}


	@Override 
	public void run(){
		Message msg = null;
		try{
			while(!_exit ){
				msg = _msgConsumer.receive(100);
				if(msg == null){
					continue;
				}
				try{
					if( !(msg instanceof BytesMessage)){
						RpcCommunicator.instance().getLogger().info("unrecognized message skipped");
						continue;
					}

					BytesMessage bytemsg = (BytesMessage)msg;
					long size = bytemsg.getBodyLength();
					byte[] data = new byte[(int)size];
					bytemsg.readBytes(data);
					RpcMessage m = RpcMessage.unmarshall(data);
					if(m!=null){
						m.conn = this;
						RpcCommunicator.instance().dispatchMsg(m);//多线程执行
					}
				}catch(Exception e){
					e.printStackTrace();
				}
			}
		}catch (Exception e){
			e.printStackTrace();
		}
		RpcCommunicator.instance().getLogger().info("Thread:"+Thread.currentThread().getId()+" terminated!");
	}



	public static boolean initMQEndpoints(String serverName,String ymlfile){

		File file = new File(ymlfile);
		if( !file.exists() ){
			return false;
		}
//		String servername = getServerName();

		try{
			Object obj = Yaml.load(file);
			HashMap<String,RpcEndPoint> ep_defs = new HashMap<String, RpcEndPoint>();
			HashMap<String,Object> node,root = (HashMap<String,Object>)obj;
			ArrayList<Object> list;
			node =(HashMap<String,Object>) root.get("common_defs");
			list =(ArrayList<Object>)node.get("endpoints");

			RpcEndPoint ep ;
			for( Object epdef:list){
				HashMap<String,Object> item = (HashMap<String,Object>)epdef;
				String name =(String) item.get("name");
				String host =(String) item.get("host");
				int port = (Integer) item.get("port");
				String address =(String) item.get("address");
				String type = (String) item.get("type");
				ep = new RpcEndPoint(name,host,port,address,type);
				ep_defs.put( name,ep);
			}
			node =(HashMap<String,Object>) root.get(serverName);
			list =(ArrayList<Object>)node.get("endpoints");

			HashMap< String,RpcConnection_QpidMQ> conns = new HashMap<String, RpcConnection_QpidMQ>();

//			ArrayList<RpcConnection_QpidMQ> connWrites = new ArrayList<RpcConnection_QpidMQ>();
//			RpcConnection_QpidMQ connRead = null;
			RpcConnection_QpidMQ conn ;
			for(Object o: list){
				HashMap<String,Object> item = (HashMap<String,Object>)o;
				String name = (String)item.get("name");
				String af = (String)item.get("af_mode");
				ep = ep_defs.get(name);
				int af_mode = RpcEndPoint.AF_READ;
				if( af.toLowerCase().equals( "af_write")){
					af_mode = RpcEndPoint.AF_WRITE;
				}
				conn = RpcConnection_QpidMQ.create(ep,af_mode);
				if(conn == null){
					System.out.println("QpidMQ create failed! " + ep.name);
					return false;
				}
				conns.put( name,conn);
			}

			node =(HashMap<String,Object>) root.get(serverName);
			list =(ArrayList<Object>)node.get("endpoint_pairs");
			for(Object o: list){
				HashMap<String,Object> item = (HashMap<String,Object>)o;
				String call = (String)item.get("call");
				String return_ = (String)item.get("return");
				conn = conns.get(call);
				RpcConnection_QpidMQ connRead = conns.get(return_);
				conn.setLoopbackMQ(connRead);
				if( connRead == null){
					System.out.println("QpidMQ not defined! "+ return_);
				}
			}

		}catch (Exception e){
			return false;
		}
		return true;
	}

}
