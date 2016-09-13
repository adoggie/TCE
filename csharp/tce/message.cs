
using System;
using System.IO;
using System.Threading;

namespace Tce {

    public class RpcMessage {
        public const int UNDEFINED = 0x00;
        public const int CALL = 0x01;
        public const int RETURN = 0x02;
        public const int TWOWAY = 0x10;
        public const int ONEWAY  = 0x20;
        public const int ASYNC   = 0x40;
        


        public const int RPC_PACKET_HDR_SIZE = 17;

        public int type = RpcConstValue.MSGTYPE_RPC;
        public int sequence = 0;            //自增序号
        public int calltype = 0;            //rpc调用方式
        public int ifidx = 0;               //调用接口编号
        public int opidx = 0;               //接口内函数编号
        public int errcode = RpcException.RPCERROR_SUCC;
        public int call_id = 0;             //调用者类型
        public int paramsize = 0;           //参数个数
        public byte[] paramstream = null;
        public RpcExtraData extra = new RpcExtraData();
        public RpcProxyBase prx = null;     
        public long timeout;
        public long issuetime;
        public RpcAsyncCallBackBase async = null;


        public RpcConnection conn;
        public RpcMessage callmsg;
        public object cookie;
        public int status;  // 0 means to send
        public RpcMessage result;
        public AutoResetEvent ev = new AutoResetEvent(false);

        public RpcMessage(int calltype = UNDEFINED) {
            this.calltype = calltype;
        }

        //从二进制流中反序列化出对象RpcMessage
        public static RpcMessage unmarshall(Stream stream){
            RpcMessage m = new RpcMessage();            
            BinaryReader reader = new BinaryReader(stream);
            try {
                m.type = RpcBinarySerializer.readByte(reader);
                m.sequence = RpcBinarySerializer.readInt(reader);
                m.calltype = RpcBinarySerializer.readByte(reader);
                m.ifidx = RpcBinarySerializer.readShort(reader);
                m.opidx = RpcBinarySerializer.readShort(reader);
                m.errcode = RpcBinarySerializer.readInt(reader);
                m.paramsize = RpcBinarySerializer.readByte(reader);
                m.call_id = RpcBinarySerializer.readShort(reader);
                if (m.extra.unmarshall(stream) == false) {
                    return null;
                }
                m.paramstream = reader.ReadBytes( (int)(stream.Length - stream.Position) );
            }
            catch (Exception e) {
                RpcCommunicator.instance().logger.error(e.ToString());
                m = null;
            }
            return m;
        }

        //刚才出去吃麦，看到一只dog在贴单子，一过去，车开走了，那个沮丧的样子哦，还一直呆在那里与正拍摄的我进行对视
        // 车子，单子，票子奋斗的dog
        public Stream marshall() {
            // to be continue.. 
            MemoryStream stream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(stream);
            RpcBinarySerializer.writeByte((byte)RpcConstValue.MSGTYPE_RPC,writer);
            RpcBinarySerializer.writeInt( this.sequence,writer);
            RpcBinarySerializer.writeByte((byte)this.calltype,writer);
            RpcBinarySerializer.writeShort((short)this.ifidx,writer);
            RpcBinarySerializer.writeShort((short)this.opidx,writer);
            RpcBinarySerializer.writeInt(this.errcode,writer);
            RpcBinarySerializer.writeByte((byte)this.paramsize,writer);
            RpcBinarySerializer.writeShort((short)this.call_id,writer);
            this.extra.marshall(stream);
            if (this.paramstream != null) {
                writer.Write(this.paramstream);
            }
            return stream;
        }
    }


    public class RpcMessageCall:RpcMessage{

        public RpcMessageCall(): base(RpcMessage.CALL){
		
	    }
	
    }


    public class RpcMessageReturn : RpcMessage{
        public RpcMessageReturn()
            : base(RpcMessage.RETURN){

        }

        public RpcMessageReturn(int seq, int errcode):this() {
            this.sequence = seq;
            this.errcode = errcode;
        }

        public void send(RpcConnection conn) {
            conn.sendMessage(this);
        }
    }


    public class RpcAsyncCallBackBase{
        //public object delta = null;
        //private string _token = null;
        //private bool _execInMainThread = false;
        private RpcAsyncContext _ctx = null;
        public RpcPromise promise;
        public object cookie;

        public RpcAsyncCallBackBase() {
            
        }

        //public RpcAsyncCallBackBase(RpcAsyncContext ctx) {
        //    _ctx = ctx;
        //}

        public RpcAsyncContext ctx {
            get{return new RpcAsyncContext(this.cookie,this.promise);}
            //set { _ctx = value; }
        }

        public virtual void callReturn(RpcMessage m1, RpcMessage m2){

        }

        public virtual void onError(int errorcode){

        }
    }


}