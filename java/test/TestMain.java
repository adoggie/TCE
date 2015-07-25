package test;

import sns_mobile.*;
import java.util.*;
import tce.*;
import java.nio.*;
import java.io.*;

public class TestMain extends ts_AsyncCallBack {
	
	@Override
	public void verify(ts_verify_r_Result_t result,RpcProxyBase proxy){
		
		System.out.println(String.format("async call back: code=%d",result.code));
	}	
	
	void test_ref(Integer i){
	 i+=Integer.valueOf(80);	
	}
	
	void test(){
		Integer x = Integer.valueOf(90);
		test_ref(x);
		byte[] aa = {1,2,3};
		byte[] bb = Arrays.copyOfRange(aa, 1, 4);
		
		System.out.println(x);
		
		Hashtable<Integer,String> as = new Hashtable<Integer,String>();
		as.put(Integer.valueOf(1), "abc");
		if(as.containsKey(Integer.valueOf(1))){
		}
		
		ByteArrayOutputStream bos = new ByteArrayOutputStream();

		try{
			DataOutputStream dos = new DataOutputStream(bos);
			System.out.println(dos.size());
			dos.writeInt(10000);
			System.out.println(dos.size());
			byte[]  bytes = bos.toByteArray();
			
			System.out.println(bytes.length);
		}catch(Exception e){
			System.out.println(e.toString());
		}
		
		ByteBuffer buf = ByteBuffer.allocate(4);
		try{
			buf.putInt(Integer.valueOf("100"));
			System.out.println(buf.limit());
			System.out.println(buf.remaining());
			System.out.println(buf.position());
	 		
			buf.limit(15);
			buf.putInt(Integer.valueOf("100"));
			System.out.println(buf.limit());
			System.out.println(buf.remaining());
			System.out.println(buf.position());
			
		
		}catch(Exception e){
			System.out.println(e.toString());
		}
		byte[] d = buf.array();
		System.out.println(d.length);
		
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		new TestMain().test();
		
		tsProxy prx = tsProxy.createWithXML("localhost", 12001);
		ts_heartbeat_p_User_t user = new ts_heartbeat_p_User_t();
		user.id = "A-12300222-999000";
		RpcCommunicator.instance().init();
		try{

			//reversed callback
			TestServant servant = new TestServant();
			RpcCommAdapter adapter = RpcCommunicator.instance().
					createAdapter("terminal", RpcConsts.MSG_ENCODE_XML);
			adapter.addServant(servant);
			prx.conn.attachAdapter(adapter);
			
			//
			ts_verify_p_User_t p1 = new ts_verify_p_User_t();
			p1.token ="TOKEN-000000001";
			
			prx.heartbeat_oneway(user);
			
			ts_verify_r_Result_t vr;
			vr = prx.verify(p1, 0);
			vr = prx.verify(p1, 4000); //超时调用
			System.out.println(vr.code);
			
			
			 
			//async call
			TestMain asyncer = new TestMain();
			prx.verify_async(p1,asyncer);
			 
			
			
			Thread.sleep(1000*1000);
		}catch(Exception e){
			System.out.println(e.toString());
		}
		
		prx.destroy();
	}

}
