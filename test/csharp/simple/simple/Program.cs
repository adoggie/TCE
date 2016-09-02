using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using Tce;
using test;
namespace simple
{

    

    class Program
    {
        static void Main(string[] args) {
           
            MemoryStream stream = new MemoryStream();
            stream.Write( new byte[10],0,10 );
            stream.Seek(0, SeekOrigin.Begin);
            stream.Write(new byte[20], 0, 20);
            //uint v = (uint)IPAddress.HostToNetworkOrder( RpcConnectionSocket.PACKET_META_MAGIC);

            RpcCommunicator.instance().logger.addLogHandler("stdout", new RpcLogHandlerStdout());
            RpcCommunicator.instance().initialize("server1");
            RpcAdapter adapter = RpcCommunicator.instance().createAdapter("adapter1");
            ServerProxy prx = ServerProxy.create("192.168.199.235",16005,false );
            Dictionary<string, string> props = new Dictionary<string, string>();
            props.Add("name","scott");
            Console.WriteLine("echo wall:" + prx.echo("hello tce! ", 30000, props));

            RpcCommunicator.instance().waitForShutdown();
            
        }
    }
}
