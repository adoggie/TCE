package tce.mq;

import org.ho.yaml.Yaml;
import tce.RpcCommunicator;
import tce.RpcConnectionAcceptor;
import tce.RpcEndPoint;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by zhangbin on 16/9/5.
 */

public class RpcConnectionAcceptorQpid extends RpcConnectionAcceptor {

    String _servername;
    String _yaml_file;




    protected RpcConnectionAcceptorQpid(String servername,String yaml){
        super();
        _servername = servername;
        _yaml_file = yaml;
    }

    public static  RpcConnectionAcceptorQpid create(String servername,String yaml ){
        RpcConnectionAcceptorQpid acceptor = new RpcConnectionAcceptorQpid(servername,yaml);
        return acceptor;
    }


    @Override
    public boolean open(){
        boolean rc = false;
        rc = initialize( _servername,_yaml_file);
        return true;
    }


    public RpcConnection_QpidMQ getConnectionByName(String name){
        return (RpcConnection_QpidMQ)getConnection( name );
    }


    /**
     * initialize()
     *  从配置文件中读取并初始化 消息队列的连接对象列表
     * @param serverName
     * @param ymlfile
     * @return
     */
    private boolean initialize(String serverName,String ymlfile){

        File file = new File(ymlfile);
        if( !file.exists() ){
            return false;
        }

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
                    RpcCommunicator.instance().getLogger().error("QpidMQ create failed! " + ep.name);
                    return false;
                }
                addConnection(name,conn);
//                _conns.put( name,conn);
//                conn.setAcceptor(this);
            }

            node =(HashMap<String,Object>) root.get(serverName);
            list =(ArrayList<Object>)node.get("endpoint_pairs");
            for(Object o: list){
                HashMap<String,Object> item = (HashMap<String,Object>)o;
                String call = (String)item.get("call");
                String return_ = (String)item.get("return");
                conn = (RpcConnection_QpidMQ)getConnection(call) ;// _conns.get(call);
                RpcConnection_QpidMQ connRead = (RpcConnection_QpidMQ) getConnection(return_); //_conns.get(return_);
                conn.setLoopbackMQ(connRead);
                if( connRead == null){
                    RpcCommunicator.instance().getLogger().error("QpidMQ not defined! "+ return_);
                }
            }

        }catch (Exception e){
            RpcCommunicator.instance().getLogger().error( e.getMessage());
            return false;
        }
        return true;
    }




}


/**
 * 以下为Qpid endpoints定义列表

 common_defs:
     endpoints:
         - name: mq_client
         host: centos66
         port: 5672
         address: mq_client;{create:always,node:{type:queue,durable:true}}
         type: qpid

         - name: mq_server
         host: centos66
         port: 5672
         address: mq_server;{create:always,node:{type:queue,durable:true}}
         type: qpid

 client:
     endpoints:
         - name: mq_client
         af_mode: AF_READ
         - name: mq_server
         af_mode: AF_WRITE

     endpoint_pairs:
         - call: mq_server
         return: mq_client

 server:
     endpoints:
         - name: mq_client
         af_mode: AF_WRITE
         - name: mq_server
         af_mode: AF_READ


 */