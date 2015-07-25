
package tce;

import tce.RpcConsts;
//import java.util.*;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import tce.RpcAsyncCallBackBase;
//import tce.RpcServantDelegate;
//import tce.RpcException;
import tce.RpcProxyBase;
import tce.RpcConnection;

public class RpcMessage{
	public static final  int CALL = 0x01;
	public static final  int RETURN = 0x02;
	public static final  int TWOWAY = 0x10;
	public static final  int ONEWAY = 0x20;
	public static final  int ASYNC = 0x40;

	public static final String EnvelopBegin="<NaviMSG";
	public static final String EnvelopClose="</NaviMSG>";
	public static final  int MAXPACKET_SIZE = 1024*1024*1;
	public static final int RPC_PACKET_HDR_SIZE = 17;

//	public String opname=""; //璋冪敤鏂规硶鍚嶇О
	//public Vector<byte[]> params = new Vector<byte[]>();
	public int type = RpcConsts.MSGTYPE_RPC;

	public int sequence = 0;
	public int calltype = 0;
	public int ifidx = 0;
	public int opidx = 0;
	public int errcode = RpcConsts.RPCERROR_SUCC;
	public int call_id = 0;
	public int paramsize = 0;
	public byte[] paramstream = null;
	public RpcExtraData extra = new RpcExtraData();

	public RpcProxyBase prx = null;
	public long timeout;
	public long issuetime;
	public RpcAsyncCallBackBase async = null;
	public RpcConnection conn = null;
	public RpcMessage callmsg = null;


	public Object cookie = null; //异步调用时传递给回调函数 2013.11.30
//	public Object delta = null;
	public int status = 0; // 0 means to send
	public RpcMessage result = null ;//
	public  RpcMessage(){

	}

	public  RpcMessage(int calltype_){
		calltype = calltype_;
		if( (calltype & CALL) !=0){
			sequence = RpcCommunicator.instance().getUniqueSequence();
		}
	}
//
//	public void addParam(byte[] bytes){
////		this.params.add(bytes);
//	}

	public byte[] marshall(){

		try{
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			dos.writeByte(RpcConsts.MSGTYPE_RPC);
			dos.writeInt(this.sequence);
			dos.writeByte(this.calltype);
			dos.writeShort(this.ifidx);
			dos.writeShort(this.opidx);
			dos.writeInt(this.errcode);
			//dos.writeByte(Integer.valueOf(params.size()).byteValue());
			dos.writeByte(this.paramsize); // dummy paramsize field,ignored
			dos.writeShort(this.call_id);
			if(this.extra.marshall(dos) == false){
				return null;
			}
			if( this.paramstream !=null){
				dos.write(this.paramstream);
			}
			return bos.toByteArray();
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}
		return null;

	}


	public static RpcMessage unmarshall(byte[] d){
		RpcMessage m = null ;
		try{
			ByteBuffer buf = ByteBuffer.wrap(d);
			buf.order(ByteOrder.BIG_ENDIAN);
			// field paramstream must be assigned!!!!!
			m = new RpcMessage();
			m.type = buf.get();
			m.sequence = buf.getInt();
			m.calltype = buf.get();
			m.ifidx = buf.getShort();
			m.opidx = buf.getShort();
			m.errcode = buf.getInt();
			m.paramsize = buf.get();
			m.call_id = buf.getShort();
			if( m.extra.unmarshall(buf) == false){
				return null;
			}
			if(d.length!=0){
				int size = d.length - (RPC_PACKET_HDR_SIZE+m.extra.size());
				m.paramstream = new byte[ size ];
				System.arraycopy(d, RPC_PACKET_HDR_SIZE + m.extra.size(), m.paramstream, 0, m.paramstream.length);
			}
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error("RpcMessage.unmarshall() failed, detail: " + e.toString());
			m = null;
		}
		return m;

		//m.paramstream = Arrays.copyOfRange(d, RPC_PACKET_HDR_SIZE, d.length);
		/*
		try{
			m = new RpcMessage();
			m.type = d.readUnsignedByte();
			m.sequence = d.readUnsignedInt();
			m.calltype = d.readUnsignedByte();
			m.ifidx = d.readUnsignedShort();
			m.opidx = d.readUnsignedShort();
			m.errcode = d.readInt();
			m.paramsize = d.readUnsignedByte(); //閼存灏楅懘鐔诲妷閼煎倿鍩堥悙鈺嬫嫹闁愁厼绻嗛崝澶庡妷閼煎倿鍩堥敓锟�	m.paramstream = new ByteArray();
			m.paramstream.writeBytes(d,d.position,d.bytesAvailable);
			m.paramstream.position = 0;
			return m;

		}catch(e:Error){
			trace(e.toString());
		}
		return null;
		//return m;

		}

		*/

	}

}

