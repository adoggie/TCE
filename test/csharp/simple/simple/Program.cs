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
            RpcPromise p = new RpcPromise();
            p.then(_ => {
                prx.echo_async("this is a sync text",
                    delegate(string result, RpcAsyncContext ctx) {
                        Console.WriteLine("echo() result:" + result);
                        ctx.promise.data = result;
                        ctx.onNext();
                        //ctx.again();
                    }, _.promise);
            }).then(_ => {
                prx.timeout_async(1, delegate(RpcAsyncContext ctx) {
                    Console.WriteLine("timeout completed!");
                    ctx.onNext();    
                },_.promise);                
            });
            RpcPromise pe = p.error(_ => {
                Console.WriteLine("async call error:"+ _.exception.ToString());
                _.onNext();
            });
            p.final(_ => {
                Console.WriteLine(" commands be executed completed!");
            });
            p.end();
        }

        void call_extradata() {

            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name", "scott");
            Console.WriteLine("echo wall:" + prx.echo("hello tce! ", 30000, props));
        }

        void init() {
            RpcCommunicator.instance().logger.addLogHandler("stdout", new RpcLogHandlerStdout());
            RpcCommunicator.instance().initialize("server1");
            //RpcCommunicator.instance().settings.callwait = 1000*1000;

            RpcAdapter adapter = RpcCommunicator.instance().createAdapter("adapter1");
            prx = ServerProxy.create("192.168.199.235", 16005, false);
            TerminalImpl impl = new TerminalImpl();
            adapter.attachConnection(prx.conn);
            adapter.addServant(impl);

        }

        void test_promise() {
            RpcPromise p = new RpcPromise();
            p.then(delegate(RpcAsyncContext ctx) {
                ctx.promise.data = "abc";
                Console.WriteLine("step 1.1");
                ctx.promise.onNext(ctx);
            }).then(delegate(RpcAsyncContext ctx) {
                Console.WriteLine("step 1.2");
                Console.WriteLine(ctx.promise.data);
                //ctx.promise.onNext(ctx);
                ctx.promise.onError(ctx);
            });
            RpcPromise p2 = p.error(delegate(RpcAsyncContext ctx) {
                //p.onNext(ctx,ctx.promise); 
                Console.WriteLine("step 2.1");
                ctx.promise.onError(ctx);
            });
            RpcPromise p3 = p2.error(delegate(RpcAsyncContext ctx) {
                Console.WriteLine("step 3.1");
                ctx.promise.onNext(ctx);
            });
            p3.then(delegate(RpcAsyncContext ctx) {
                Console.WriteLine("step 2.2");
                ctx.promise.onNext(ctx);
            });
            
            p.then(delegate(RpcAsyncContext ctx) {
                Console.WriteLine("step 1.3");
                ctx.promise.onNext(ctx);
            }).final(delegate(RpcAsyncContext ctx) {
                Console.WriteLine("final.");
                Console.WriteLine(ctx.promise.data);
                Console.ReadKey(true);
            }).end();

        }

        static void Main(string[] args) {

            
            Program program = new Program();
            //program.test_promise();
            //return;

            program.init();
            for (int n = 0; n < 100; n++) {
                //program.two_way();
                //program.one_way();
                program.async_call();
                //program.bidirection();

                System.Threading.Thread.Sleep(1000);
            }
            RpcCommunicator.instance().waitForShutdown();
            
        }
    }
}
