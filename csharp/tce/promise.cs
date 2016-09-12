

using System.Collections.Generic;

/*
how to use:
 * 
 * 
 * RpcPromise p = new RpcPromise();
 *  p.then( delegate(RpcAsyncContext ctx){
 *      prx.echo_async(text,delegate(string result,RpcAsyncContext ctx){
 *              ctx.promise.data = result;  // pass result to next then
 *          },ctx.promise);
 *      });
 *  p.then( delegate(RpcAsyncContext ctx){
 *      Console.Writeln(" async call return :" + ctx.promise.data; 
 * });
 *  p.error( delegate(RpcAsyncContext ctx,RpcException e){
 *      Consoel.Writeln(" async call failed!"+ e.ToString());
 *  });
 *  p.end();
 * 
 * */
namespace Tce {
    public class RpcPromise {
        object _data;
        private List<OnNext> _sucesslist = new List<OnNext>();
        private OnNext _finally; 
        private List< KeyValuePair<RpcPromise,OnNext> > _errorlist = new List<KeyValuePair<RpcPromise, OnNext>>();
        
        public delegate void OnNext(RpcAsyncContext ctx);

        private RpcPromise _upPromise;
        private RpcPromise _nextPromise;
        private OnNext _lastPoint;

        private int _id = 0;
        private static int seqID = 1;

        public RpcPromise() {
            _id = seqID++;
        }

        public int id {
            get { return _id; }
        }

        /**
         * onNext()
         * promise下一个处理
         * 同一个promise中 step1 -> step2 
         * 下一个promise 跳转到上级 promise
         */
        public void onNext(RpcAsyncContext ctx,RpcPromise from = null) {
            if (true) {
                if (from != null && from._lastPoint != null)
                {
                    int index = _sucesslist.IndexOf(from._lastPoint);
                    _sucesslist.RemoveRange(0,index+1);                    
                }

                if (_sucesslist.Count == 0) {
                    onFinally(ctx);
                    return;
                }
                OnNext next = null;
                next = _sucesslist[0];
                _sucesslist.RemoveAt(0);
                if ( next != null) {
                    next( ctx );
                }                
            }
        }

        private void onFinally(RpcAsyncContext ctx) {
            if (_finally != null) {
                _finally(ctx);
            }
            if (_nextPromise != null) {
                _nextPromise.onNext(ctx,this);
            }
        }

        public void onError(RpcAsyncContext ctx)
        {           
            if (_errorlist.Count == 0)
            {
                onFinally(ctx);
                return;
            }
            // pick out one fork-promise
            KeyValuePair<RpcPromise, OnNext> kv = _errorlist[0];
            OnNext succ = kv.Value;
            RpcPromise next = kv.Key;
            _errorlist.RemoveAt(0);
            // scan list and remove all nodes which's depth of node is less than promise. 
            int index = _sucesslist.IndexOf(succ);
            _sucesslist.RemoveRange(0, index + 1);

            if (next != null) {
                ctx.promise = next;
                next.onNext(ctx);
            }
        }

        public object data {
            get{ return _data;}
            set { _data = value; }
        }

        /**
         * then()
         * if both succ and error are null , start chain. 
         * 
         */
        public RpcPromise then(OnNext succ) {
            if(true){
               _sucesslist.Add(succ); 
            }
            return this;
        }

        /**
         *  at here  , new promise be created as Error processing fork. 
         *  you can promise.wait util the error-routine return. 
         */
        public RpcPromise error(OnNext error ) {
            RpcPromise promise = new RpcPromise();
            if(true) {
                OnNext succ = null;
                
                if (_sucesslist.Count != 0) {
                    succ = _sucesslist[_sucesslist.Count - 1]; // select last OnNext
                }
                                
                KeyValuePair<RpcPromise,OnNext> kv = new KeyValuePair<RpcPromise, OnNext>(promise,succ);
                _errorlist.Add( kv );
                promise._nextPromise = this;
                promise.then(error);
            }
            return promise;
        }

        public RpcPromise final(OnNext next ) {
            _finally = next;
            return this;
        }

        public void join(RpcPromise promise) {
            promise._nextPromise = this; // 
            OnNext last = null;
            if (_sucesslist.Count != 0) {
                last = _sucesslist[_sucesslist.Count - 1];
            }
            promise._lastPoint = last;
        }

        public RpcPromise end() {
            if(true){
                if (_sucesslist.Count != 0) {
                    OnNext step = _sucesslist[0];
                    _sucesslist.RemoveAt(0);
                    step( new RpcAsyncContext(null,this));
                }
                return this;
            }
        }

    }

}