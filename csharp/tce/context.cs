
using System;
using System.Collections.Generic;

namespace Tce {
    public class RpcContext {
        public RpcMessage msg;
        public RpcContext() {
            
        }
    }

    public class RpcAsyncContext {        
        public object cookie;
        public RpcProxyBase proxy;
        public RpcPromise promise;
        public RpcException exception;

        public RpcAsyncContext( object cookie,RpcPromise promise) {
            this.cookie = cookie;
            this.promise = promise;
        }

        public RpcAsyncContext() {
            
        }

        public void onNext() {
            this.promise.onNext(this);
        }

        public void onError() {
            this.promise.onError(this);
        }

        public void again() {
            this.promise.again(this);
        }
    }

}