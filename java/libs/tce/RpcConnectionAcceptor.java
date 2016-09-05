package tce;

/**
 * Created by zhangbin on 16/9/5.
 */
public class RpcConnectionAcceptor {

    boolean _is_open = false;
    RpcAdapter _adapter = null;

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

}
