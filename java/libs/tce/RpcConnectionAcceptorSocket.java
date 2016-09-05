package tce;

/**
 * Created by zhangbin on 16/9/5.
 */
public class RpcConnectionAcceptorSocket extends RpcConnectionAcceptor {
//    public class RpcEndpointSocket extends RpcEndPoint{
//
//    }


    public static  RpcConnectionAcceptorSocket create(RpcEndPoint ep){
        return  null;
    }

    @Override
    public boolean open(){
        return true;
    }
}
