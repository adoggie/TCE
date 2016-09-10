package com.sw2us.android;

import java.util.*;

//import tce;
import java.nio.*;
import java.io.*;
import sns.*;
import tce.RpcContext;
import tce.RpcProxyBase;
import tce.android.*;
import android.widget.*;



public class Main {
	static final String TARGET_HOST="192.168.14.101";
	static final int TARGET_PORT= 16005;
	
	class Terminal extends sns.ITerminal{
		public Terminal(){
			super();
		}

		@Override
		public void onNotifyMessage(String notify, RpcContext ctx) {
			super.onNotifyMessage(notify, ctx);
			Main.instance().text.setText("msg:"+notify+" from server!");
		}


		
	}
	
	TextView text = null; 
	
	ICtrlServerProxy prxCtrlServer = null;
//	IGatewayProxy prxGateway = null;
	public Main(){
		prxCtrlServer = ICtrlServerProxy.create(TARGET_HOST,TARGET_PORT,true); // ssl proxy
//		prxGateway = IGatewayProxy.createWithProxy(prxCtrlServer); //
	}
	 int count = 0;
	void test_normal(){
		try{
			long start,end;
			
			start = System.currentTimeMillis();
			
			for(int n=0;n<1;n++){
//				Boolean result = prxCtrlServer.changeUserPasswd("123", "456");
				prxCtrlServer.register_async("scott", "jetty", new ICtrlServer_AsyncCallBack() {
					@Override
					public void register(String result, RpcProxyBase proxy, Object cookie) {
						super.register(result, proxy, cookie);
						System.out.println("register return:" + result);
						Main.this.text.setText(result.toString());
					}
				}, null);
//				String s ;
//				prxGateway.description_async(new IGateway_AsyncCallBack(){
//
//					@Override
//					public void description(String result, RpcProxyBase proxy, Object cookie) {
//						super.description(result, proxy, cookie);
//						Main.this.text.setText(result.toString());
//					}
//
//
//				},null);
//				System.out.println(s.length() + ok.toString());
//				System.out.println(String.format("login call , return: <%d>.", n)+ result);
			}
			end = System.currentTimeMillis();
			System.out.print("elapsed:"+( end-start)/1000.0);
			
		}catch(Exception e){
			System.out.println(e.toString());
		}
	}
	
	void test_oneway(){
		try{
//			prxCtrlServer.userOnline("abc", 10000, null);
//			prxGateway.heartbeat_oneway(null);
		}catch(Exception e){
			System.out.println(e.toString());
		}
	}

	void test_reverse(){
		try{
//			prxCtrlServer.userOffline_oneway("scott", null);
		}catch(Exception e){
			System.out.println(e.toString());
		}
	}
	
	void test(TextView showtext){
		this.text = showtext ;
		test_normal();
//		test_reverse();
	}
	
	void init(){
		System.out.println("Tce Test start..");
		tce.RpcCommAdapter adapter =  tce.RpcCommunicator.instance().createAdapterWithProxy("local", prxCtrlServer);
		Terminal servant = new Terminal();
		adapter.addServant(servant);
		
	}
	
	static Main app = null;
	
	protected static Main instance(){
		if(app == null){
			RpcCommunicator_Android.instance().init(new HashMap<String, String>());
			app = new Main();
			app.init();
		}
		return app;
	}
//	public static void main(String[] args) {
//		
////		tce.RpcCommunicator.instance().waitForShutdown();
//	}

}
