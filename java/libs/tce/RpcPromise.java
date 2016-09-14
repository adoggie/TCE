package tce;

import tce.utils.KeyValuePair;

import java.util.Vector;

/**
 * Created by zhangbin on 16/9/13.
 */
public class RpcPromise {

    static long seqID = 1;

    private long _id = 0;
    private RpcPromise _nextPromise;
    private RpcPromise _upPromise;
    private Object _data;
    private Vector<Behavior> _successlist = new Vector<Behavior>();
    private Behavior _finanlly;
    private Behavior _lastPoint;
    private Vector<KeyValuePair<RpcPromise,Behavior>> _errorlist = new Vector<KeyValuePair<RpcPromise, Behavior>>();


    public interface Behavior{
        void onNext(RpcAsyncContext ctx);
    }

    public RpcPromise(){
        _id = seqID++;
    }

    public long getId(){
        return _id;
    }

    public void onNext(RpcAsyncContext ctx,RpcPromise from){
        if( from !=null && from._lastPoint != null){
            int index = _successlist.indexOf(from._lastPoint);
            _successlist.subList(0,index+1).clear();
        }
        if(_successlist.size() == 0){
            onFinally(ctx);
            return ;
        }
        Behavior next = null;
        next = _successlist.remove(0);
        if( next != null){
            next.onNext(ctx);
        }
    }

    private void onFinally(RpcAsyncContext ctx){
        if(_finanlly != null){
            _finanlly.onNext(ctx);
        }
        if( _nextPromise != null){
            _nextPromise.onNext(ctx,this);
        }
    }

    public void onNext(RpcAsyncContext ctx){
        onNext(ctx,null);
    }

    public void onError(RpcAsyncContext ctx){
        if( _errorlist.size() == 0 ){
            onFinally(ctx);
            return;
        }
        KeyValuePair<RpcPromise,Behavior> kv = _errorlist.remove(0);
        int index = _successlist.indexOf(kv.getValue());
        _successlist.subList(0,index+1).clear();

        ctx.promise = kv.getKey();
        ctx.promise.onNext(ctx);  // drive into next
    }

    public Object getData(){
        return _data;
    }

    public void setData(Object data){
        _data = data;
    }


    public RpcPromise then(Behavior next){
        _successlist.add(next);
        return this;
    }

    public RpcPromise error(Behavior next){
        RpcPromise promise = new RpcPromise();
        Behavior last = null;
        if( _successlist.size() != 0){
            last = _successlist.lastElement();
        }
        KeyValuePair<RpcPromise,Behavior> kv = new KeyValuePair<RpcPromise,Behavior>(promise,last);
        _errorlist.add(kv);
        promise._nextPromise = this;
        promise.then( next );

        return promise;
    }

    public RpcPromise final_( Behavior next){
        _finanlly = next;
        return this;
    }

    public void join(RpcPromise promise){
        promise._nextPromise = this;
        Behavior last = null;
        if( _successlist.size() !=0){
            last = _successlist.lastElement();
        }
        promise._lastPoint = last;
    }

    public RpcPromise end(){
        if( _successlist.isEmpty() == false){
            Behavior next = _successlist.remove(0);
            next.onNext( new RpcAsyncContext(null,this));
        }
        return this;
    }

}
