using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using Tce;
using test;
namespace simple
{
    class TerminalImpl : ITerminal {
        public override void onMessage(string message, RpcContext ctx) {
            base.onMessage(message, ctx);
            Console.WriteLine( message);
        }
    }
    

    class Program {
        private ServerProxy prx = null;

        void bidirection() {
            prx.bidirection_oneway();
        }

        void two_way() {
            Console.WriteLine("echo wall:" + prx.echo("hello tce! "));
        }

        void one_way() {
            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name", "scott");
            prx.heartbeat_oneway("hello man!",props);
        }

        void async_call() {
            prx.echo_async("this is async test.", delegate(string result, RpcProxyBase proxy, object cookie) {
                Console.WriteLine("you recieved one async result:"+ result + " cookie is:" + cookie);                
            },null,"9680");
        }

        void call_extradata() {

            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name", "scott");
            Console.WriteLine("echo wall:" + prx.echo("hello tce! ", 30000, props));
        }

        void init() {
            RpcCommunicator.instance().logger.addLogHandler("stdout", new RpcLogHandlerStdout());
            RpcCommunicator.instance().initialize("server1");
            RpcCommunicator.instance().settings.callwait = 1000*1000;

            RpcAdapter adapter = RpcCommunicator.instance().createAdapter("adapter1");
            prx = ServerProxy.create("192.168.199.235", 16005, false);
            TerminalImpl impl = new TerminalImpl();
            adapter.attachConnection(prx.conn);
            adapter.addServant(impl);

        }

        static void Main(string[] args) {
            Program program = new Program();
            program.init();
            for (int n = 0; n < 1000; n++) {
                program.two_way();
                program.one_way();
                program.async_call();
                program.bidirection();

                System.Threading.Thread.Sleep(1000);
            }
            RpcCommunicator.instance().waitForShutdown();
            
        }
    }
}
