
using System;

namespace Tce {

   public class RpcProxyBase {
       public RpcConnection conn = null;
       public object delta = null;

       public RpcProxyBase(){

       }
       
       /**
        * 
        */
       public void setToken(string token){
           if (conn != null){
               conn.close();
               conn.setToken(token);
           }
       }
    }

}