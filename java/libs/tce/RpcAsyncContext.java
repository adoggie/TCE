package tce;

/**
 * Created by zhangbin on 16/9/13.
 */
public class RpcAsyncContext {
    public RpcPromise promise;
    public RpcException exception;
    public Object cookie;

    public RpcAsyncContext(Object cookie,RpcPromise promise){
        this.cookie = cookie;
        this.promise = promise;
    }

}
