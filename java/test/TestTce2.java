package test;


import java.util.*;

import tce.*;

import java.nio.*;
import java.io.*;
import sns_service.*;

//测试链接到gwa

/*
 * 第一次登录到gwa之后，必须稍微停顿几十毫秒，gwa会绑定链接，然后再发送rpc请求
 * 
 * 
 */

public class TestTce2  {
	ICtrlServerProxy ctsprx = null;
	IGatewayAdapterProxy gwaprx = null;
	ILocationServerProxy locprx = null;
	IAuthServiceProxy authprx = null; //认证服务
	IMessagingServiceProxy msgprx = null;
	IUserServiceProxy userprx = null;
	
	TestTce2(){
		RpcCommunicator.instance().init();
		authprx = IAuthServiceProxy.create("127.0.0.1", 4004);
//		ctsprx = ICtrlServerProxy.create("127.0.0.1", 4002);
		gwaprx = IGatewayAdapterProxy.create("127.0.0.1",4002);
//		gwaprx = IGatewayAdapterProxy.createWithProxy(ctsprx);
	//	authprx = IAuthServiceProxy.createWithProxy(gwaprx);
		msgprx = IMessagingServiceProxy.createWithProxy(gwaprx);
		userprx = IUserServiceProxy.createWithProxy(gwaprx);
	}
	
	private String token = "";
	void test_auth(){
		long start = System.currentTimeMillis()/1000;
		
		for(int n=0;n<1;n++){
			try{
				authprx.userLogin_async("test1","123456", 1, new IAuthService_AsyncCallBack(){
					@Override
					public void userLogin(String result, RpcProxyBase proxy) { 
						System.out.println("login result:"+result);
						token = result;
						TestTce2.this.test_socket();
					}
					
				}, null);
				//Thread.sleep(500);
			}catch(Exception e){
				RpcCommunicator.instance().getLogger().error(e.toString());
			}
			
		}
		long end= System.currentTimeMillis()/1000;
		System.out.println(String.format("time elapsed:%d", end-start));
	}
	
	void test_socket(){
		try{
			
			
//			locprx = ILocServerProxy.createWithProxy(ctsprx);
//			ctsprx.getUserList_async(new Vector<String>(), new ICts_AsyncCallBack(){
//				@Override
//				public void getUserList(String result, RpcProxyBase proxy) {
//					RpcCommunicator.instance().getLogger().debug(result);
//				}
//				
//			}, null);
			
			//String token="AAAAAjI4AAAABXRlc3QxAAAAAFDoQbsAAAAAUOhPywAAAAA=";
			if( token.equals("") ){
				return ;
			}
			
			gwaprx.login_async(token, new IGatewayAdapter_AsyncCallBack(){
				@Override
				public void login(CallReturn_t result, RpcProxyBase proxy) {
					RpcCommunicator.instance().getLogger().debug(result.value);
					//test_auth();
					TestTce2.this.test_userservice();
					try{
						Thread.sleep(200);
					}catch(Exception e){
						
					}
				}
				
			}, null);
//			
			
//			test_auth();
			Thread.sleep(1000*2000000);
		}catch(Exception e){
			RpcCommunicator.instance().getLogger().error(e.toString());
		}
	}
	
	void sendMesage(){
		//msgprx
		Vector<String> targets = new Vector<String>();
		targets.add(String.valueOf(1));
		MimeMessage_t msg = new MimeMessage_t();
		msg.type = 1;
		msg.text.text = "abc";
		try{
			msgprx.sendMessage_oneway(targets, 1, msg, null);
		}catch(Exception e){
			
		}
	}
	
	ICtrlServer_AsyncCallBack ctrlserv_async = new ICtrlServer_AsyncCallBack(){

		@Override
		public void registerUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.registerUser(result, proxy);
		}

		@Override
		public void deleteUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.deleteUser(result, proxy);
		}

		@Override
		public void dispatchGWA(Vector<ServiceURI_t> result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.dispatchGWA(result, proxy);
		}

		@Override
		public void dispatchTalkingServer(Vector<ServiceURI_t> result,
				RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.dispatchTalkingServer(result, proxy);
		}

		@Override
		public void callReturn(RpcMessage m1, RpcMessage m2) {
			// TODO Auto-generated method stub
			super.callReturn(m1, m2);
		}
		
	};
	
	IUserService_AsyncCallBack async =  new IUserService_AsyncCallBack(){

		@Override
		public void getUserInfo(UserInfo_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUserInfo(result, proxy);
		}

		@Override
		public void updateUserInfo(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.updateUserInfo(result, proxy);
		}

		@Override
		public void changeUserPasswd(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.changeUserPasswd(result, proxy);
		}

		@Override
		public void getFriendGroups(Vector<UserGroupInfo_t> result,
				RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getFriendGroups(result, proxy);
			for(UserGroupInfo_t g: result){
				System.out.println(String.format("id:%s, name:%s",g.id,g.name));
			}
		}

		@Override
		public void getFriendsInGroup(Vector<UserInfo_t> result,
				RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getFriendsInGroup(result, proxy);
			System.out.println("getFriendsInGroup()");
			for(UserInfo_t user : result){
				System.out.println( String.format("id:%s, username:%s,name:%s,age:%d,sex:%d,phone:%s,city:%s,address:%s,status:%d",
							user.id,user.username,user.name,user.age,user.sex,user.phone,user.city,user.address,user.status) );
			}
		}

		@Override
		public void getAllFriends(Vector<UserInfo_t> result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getAllFriends(result, proxy);
			for(UserInfo_t user : result){
				System.out.println( String.format("id:%s, username:%s,name:%s,age:%d,sex:%d,phone:%s,city:%s,address:%s,status:%d",
							user.id,user.username,user.name,user.age,user.sex,user.phone,user.city,user.address,user.status) );
			}
		}

		@Override
		public void getUserDetail(UserInfoDetail_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUserDetail(result, proxy);
		}

		@Override
		public void renameFriendName(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.renameFriendName(result, proxy);
		}

		@Override
		public void getUserInfoList(Vector<UserInfo_t> result,
				RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUserInfoList(result, proxy);
		}

		@Override
		public void createGroup(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.createGroup(result, proxy);
			System.out.println(String.format("succ:%s, code:%d ,value:%s",result.error.succ.toString(),result.error.code,result.value));
		}

		@Override
		public void deleteGroup(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.deleteGroup(result, proxy);
		}

		@Override
		public void addGroupUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.addGroupUser(result, proxy);
		}

		@Override
		public void removeGroupUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.removeGroupUser(result, proxy);
		}

		@Override
		public void removeFriend(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.removeFriend(result, proxy);
		}

		@Override
		public void getTeams(Vector<TeamInfo_t> result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getTeams(result, proxy);
			for(TeamInfo_t team: result ){
				System.out.println(String.format("id:%s,name:%s,desc:%s",team.id,team.name,team.desc));
			}
		}

		@Override
		public void getUsersInTeam(Vector<UserInfo_t> result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUsersInTeam(result, proxy);
			for(UserInfo_t user : result){
				System.out.println( String.format("id:%s, username:%s,name:%s,age:%d,sex:%d,phone:%s,city:%s,address:%s,status:%d",
							user.id,user.username,user.name,user.age,user.sex,user.phone,user.city,user.address,user.status) );
			}
		}

		@Override
		public void addTeamUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.addTeamUser(result, proxy);
		}

		@Override
		public void removeTeamUser(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.removeTeamUser(result, proxy);
		}

		@Override
		public void exitTeam(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.exitTeam(result, proxy);
		}

		@Override
		public void createTeam(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.createTeam(result, proxy);
		}

		@Override
		public void deleteTeam(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.deleteTeam(result, proxy);
		}

		@Override
		public void updateTeamInfo(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.updateTeamInfo(result, proxy);
		}

		@Override
		public void inviteFriend(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.inviteFriend(result, proxy);
		}

		@Override
		public void getMessageLogList(QueryMessageLogResult_t result,
				RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getMessageLogList(result, proxy);
		}

		@Override
		public void getUserStatus(CallReturn_t result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUserStatus(result, proxy);
		}

		@Override
		public void getUserStatusList(Vector<UserStatus_t> result, RpcProxyBase proxy) {
			// TODO Auto-generated method stub
			super.getUserStatusList(result, proxy);
			for(UserStatus_t s:result){
				System.out.println(String.format("userid:%s, status:%d",s.userid,s.status));
			}
		}

		@Override
		public void callReturn(RpcMessage m1, RpcMessage m2) {
			// TODO Auto-generated method stub
			super.callReturn(m1, m2);
		}
		
	};
	
	void test_userservice(){
		UserGroupInfo_t ugi = new UserGroupInfo_t();
		ugi.name = "new-group2 中国";
		
		try{
//		
//			userprx.createGroup_async(ugi,async,null);
			
//			userprx.deleteGroup_async("10", new IUserService_AsyncCallBack(){
//				@Override
//				public void deleteGroup(CallReturn_t result, RpcProxyBase proxy) {
//					System.out.println(result.error.code);
//				}				
//			},null);
			
			
//			userprx.getFriendGroups_async(async, null);
			userprx.getAllFriends_async(async, null);
//			userprx.addGroupUser_async("85", "30", async, null);
//			userprx.getFriendsInGroup_async("85", async, null);
//			userprx.removeGroupUser_async("85", "30", async, null);
			
			TeamInfo_t team = new TeamInfo_t();
			team.name = "shanghai";
			team.desc = "team-group shanghai 中国";
//			userprx.createTeam_async(team, async, null);
//			userprx.getTeams_async(async, null);
//			userprx.deleteTeam_async("91", async, null);
//			userprx.getUsersInTeam_async("92", async, null);
//			userprx.renameFriendName_async("29","美丽的姑娘",async,null);
//			userprx.removeFriend_async("30", async, null);
//			userprx.removeTeamUser_async("92","29",async,null);
//			userprx.addTeamUser_async("92", "29", async, null);
			team.id = "92";
//			userprx.updateTeamInfo_async(team, async, null);
//			userprx.deleteTeam_async("92", async, null);
//			userprx.setUserStatus_oneway(1, null);
//			userprx.getUserStatus_async(async, null);
			Vector<String> ids = new Vector<String>();
			ids.add("28");
			ids.add("29");
			ids.add("30");
//			for(int n=0;n<100;n++)
//			userprx.getUserStatusList_async(ids, async, null);
			
			
			UserRegisterInfo_t reginfo = new UserRegisterInfo_t();
			reginfo.name = "啊管";
			reginfo.passwd ="1233456";
			reginfo.email = "aguan@sw2us.com";

			//			ctsprx.registerUser_async(reginfo, ctrlserv_async, null);
//			userprx.changeUserPasswd_async("1", "123456", async, null);
			
			UserInfo_t ui = new UserInfo_t();
			ui.age = 10;
			ui.name = "aguan.didi";
			ui.city = "shanghai";
			ui.address = "pujing ...";
			ui.email = "24509826@qq.com";
			ui.phone ="13916624477";
		
//			userprx.updateUserInfo_async(ui, async, null);
//			userprx.getUserInfo_async(async, null);
			
		
		}catch(Exception e){
			System.out.println(e.toString());
		}
	}
	
	static TestTce2  testtce = null;
	public static void main(String[] args) {
		testtce = new TestTce2();
		//testtce.test_socket();
		testtce.test_auth();
		try{
			Thread.sleep(1000*1000);
		}catch(Exception e){
			
		}
		//TestTce2 test = new TestTce2();
		//testtce.test_auth();
		
		
	
	}

}
