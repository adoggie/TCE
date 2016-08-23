
using  System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net;


/*
 *    重写和隐藏的定义:
            重写：基类方法声明为virtual(虚方法)，派生类中使用override申明此方法的重写.
            隐藏：基类方法不做申明（默认为非虚方法），在派生类中使用new声明此方法的隐藏。
            
            自己的理解:
            比如父类A,有个方法标记为virtual,a(){}子类B继承A,也声明一个方法a(){}   
            如果B里面的a()使用override,那么访问A的方法时实际上调用了B里面声明的方法,相当于A的方法被覆盖了,new就不是,
            访问A的a还是A里面定义的方法,访问B就是B里面定义的方法.
            说白了：new是覆盖，override是重载，“覆盖”并不意味着“删除”，但“重载”意味着“删除”，
            这就是“覆盖”和“重载”的区别  
 * 
 */
namespace Tce{

    abstract class RpcLogHandler {
        public virtual bool open() {
            return false;
        }

        public virtual void close() {
            
        }

        public virtual void write(string msg) {
            
        }
    }

    //文件输出
    class RpcLogHandlerFile : RpcLogHandler {
        public override bool open()
        {
            return false;
        }

        public override void close()
        {

        }

        public override void write(string msg)
        {

        }
    }

    //终端输出
    class RpcLogHandlerStdout : RpcLogHandler {
        public override bool open()
        {
            return false;
        }

        public override void close()
        {

        }

        public override void write(string msg)
        {
            lock (this) {
                Console.WriteLine(msg);
            }
        }
    }

    //通过udp网络发送日志
    class RpcLogHandlerUdp : RpcLogHandler {
        private IPEndPoint recvEp;
        public RpcLogHandlerUdp(string name, string host, int port) {
            
        }
        public override bool open()
        {
            return false;
        }

        public override void close()
        {

        }

        public override void write(string msg)
        {
            lock (this)
            {
                Console.WriteLine(msg);
            }
        }
    }


    class RpcLogger {
        public enum LOG_TYPE {
            NONE    = 0,   
            DEBUG   = 1,
            INFO    = 2,
            WARN    = 3,
            ERROR   = 4,
        }

        private LOG_TYPE _loglevel = LOG_TYPE.NONE;
        private string _name;

        private Dictionary<string, RpcLogHandler> _loghandlers;

        static RpcLogger logger;

        public static RpcLogger instance() {
            if (RpcLogger.logger == null) {
                RpcLogger.logger = new RpcLogger();
            }
            return RpcLogger.logger;
        }

        public static RpcLogger create(string name) {
            RpcLogger logger = new RpcLogger(name);
            return logger;

        }
        
        public string name {
            get { return _name; }
            set { _name = value; }
        }

        private RpcLogger(string name = "" ) {
            this.name = name;
            _loglevel = LOG_TYPE.DEBUG;
            _loghandlers = new Dictionary<string, RpcLogHandler>();
        }


        public RpcLogger addLogHandler(string name, RpcLogHandler handler) {
            handler.open();
            _loghandlers.Add(name,handler);
            return this;
        }

        public RpcLogger removeLogHandler(string name) {
            if (_loghandlers.ContainsKey(name)) {
                _loghandlers.Remove(name);
            }
            return this;
        } 

        public RpcLogger setLevel(LOG_TYPE type) {
            _loglevel = type;
            return this;
        }

        public RpcLogger debug(string msg) {            
            return  print(msg, LOG_TYPE.DEBUG);
        }

        public RpcLogger info(string msg) {
            return print(msg, LOG_TYPE.INFO);
        }

        public RpcLogger warn(string msg) {
            return print(msg, LOG_TYPE.WARN);
        }

        public RpcLogger error(string msg) {
            return print(msg, LOG_TYPE.ERROR);
        }

        public RpcLogger print(string msg, LOG_TYPE type) {
            if (_loglevel > type) {
                return this;
            }
            string typestr = "";
            if (type == LOG_TYPE.DEBUG) typestr = "DEBUG";
            if (type == LOG_TYPE.INFO) typestr = "INFO";
            if (type == LOG_TYPE.WARN) typestr = "WARN";
            if (type == LOG_TYPE.ERROR) typestr = "ERROR";

            
            msg = string.Format("{0} {1}  {2}", DateTime.UtcNow,typestr,msg);

            foreach ( KeyValuePair<string,RpcLogHandler> kv in this._loghandlers) {
                kv.Value.write( msg );
            }
            return this;
        }
    }

}