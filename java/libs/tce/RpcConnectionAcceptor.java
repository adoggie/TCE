package tce;



import java.util.HashMap;

/**
 * Created by zhangbin on 16/9/5.
 */
public class RpcConnectionAcceptor {

    boolean _is_open = false;
    RpcAdapter _adapter = null;
    private HashMap<String,RpcConnection> _conns = new HashMap<String,RpcConnection>();

    protected RpcConnectionAcceptor(){

    }

    public void setAdapter(RpcAdapter adapter){
        _adapter = adapter;
    }

    public RpcAdapter  getAdapter(){
        return _adapter;
    }

    public boolean isOpen(){
        return _is_open;
    }

    public boolean open(){
        return false;
    }

    public void close(){

    }

    public void addConnection(String name,RpcConnection conn){
        _conns.put( name,conn);
        conn.setAcceptor(this);
    }

    public  RpcConnection getConnection(String name){
        return _conns.get(name);
    }

    public void removeConnection(String name){
        if( _conns.containsKey(name) ){
            _conns.remove(name);
        }
    }

}
