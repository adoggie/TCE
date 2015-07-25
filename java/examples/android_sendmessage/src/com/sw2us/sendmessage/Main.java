package com.sw2us.sendmessage;

import android.widget.TextView;
import android.widget.Toast;
import sns.*;
import tce.RpcCommunicator;
import tce.RpcContext;
import tce.RpcLogger;
import tce.RpcProxyBase;
import tce.android.*;

//import tce;


public class Main {
	static final String TARGET_HOST="192.168.1.112";
	static final int TARGET_PORT= 12002;
	public static final String CURRENT_USER_ID = "A1003";
	MyActivity mainview = null;
	class Terminal extends sns.ITerminal{
		public Terminal(){
			super();
		}

		@Override
		public void onMessage(Message_t message, RpcContext ctx) {
			super.onMessage(message, ctx);
			TextView msgview = (TextView)mainview.findViewById(R.id.textMessage);
//			Main.instance().text.setText("message:"+ message.content +" from user:" + message.sender_id);
			msgview.setText(message.content + "\n"+ "from user:" + message.sender_id);
		}
		
	}
	
	TextView text = null; 
	IMessageServerProxy prxServer = null;
	ITerminalGatewayServerProxy prxGateway = null;

	public Main(){
		prxGateway = ITerminalGatewayServerProxy.create(TARGET_HOST,TARGET_PORT,false); // ssl proxy
		prxServer = IMessageServerProxy.createWithProxy(prxGateway); //
		prxServer.setToken(CURRENT_USER_ID);

	}



	void run(final  MyActivity mainview,TextView showtext){
		this.text = showtext ;
		this.mainview = mainview;
		try{
			TextView view = (TextView) mainview.findViewById(R.id.editTarget);
			String target_id = view.getText().toString();
			view = (TextView)mainview.findViewById(R.id.editContent);
			String content = view.getText().toString();
			if(content.trim().length() == 0){
				Toast.makeText(mainview,"content is null",Toast.LENGTH_SHORT).show();
				return;
			}
			Message_t msg = new Message_t();
			msg.sender_id = CURRENT_USER_ID;
			msg.content = content;


			prxServer.postMessage_async(target_id,msg,new IMessageServer_AsyncCallBack(){
				@Override
				public void postMessage(RpcProxyBase proxy, Object cookie) {
					Toast.makeText(mainview,"server got message!",Toast.LENGTH_SHORT).show();
				}
			});
		}catch (Exception e){
			System.out.println(e.toString());
		}
	}
	
	void init(){
		System.out.println("Tce Test start..");
		tce.RpcCommAdapter adapter =  tce.RpcCommunicator.instance().createAdapterWithProxy("local", prxGateway);
		Terminal servant = new Terminal();
		adapter.addServant(servant);
	}
	
	static Main app = null;
	
	protected static Main instance(){
		if(app == null){
			RpcCommunicator_Android.instance().init("test",null);
			app = new Main();
			app.init();
		}
		return app;
	}


}
