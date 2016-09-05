package tce.android;

import java.io.InputStream;
//import java.net.InetSocketAddress;
//import java.net.Socket;
//import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.io.*;
import java.net.*;
//import javax.net.ssl.*;
import java.util.*;


import org.apache.http.HttpResponse;  
//import org.apache.http.client.ClientProtocolException;  
import org.apache.http.client.entity.UrlEncodedFormEntity;  
//import org.apache.http.client.methods.HttpGet;  
import org.apache.http.client.methods.HttpPost;  
import org.apache.http.impl.client.DefaultHttpClient;  
import org.apache.http.message.BasicNameValuePair;  
import org.apache.http.protocol.HTTP;  
import org.apache.http.util.EntityUtils;  
import org.apache.http.message.BasicHeader;


//import tce.RpcAdapter;
import tce.RpcCommunicator;
import tce.RpcConnection;
import tce.RpcMessage;
import tce.RpcMessageXML;
import tce.RpcConsts;



public class RpcConnection_Http extends  RpcConnection  {
	
	
	protected String _method; // must be GET or POST
	protected String _prefix;
	public RpcConnection_Http(String host,String method){
		super(host,0);
		_type = RpcConsts.CONNECTION_HTTP;
		_method = method;
		//_prefix = prefix;
	}
	/*
	public String getMethodType(){
		return _method;
	}
	
	private boolean decodeMsg(String xml){
		RpcMessage m;
		m = RpcMessageXML.unmarshall(xml.getBytes());
		if(m!=null){
			m.conn = this;
			this.dispatchMsg(m);
			return true;
		}
		return false;
	}

	@Override 
	protected void dispatchMsg(RpcMessage m){
		RpcAsyncCommThread.instance().dispatchMsg(m);
	}
	

	private boolean sendGet(RpcMessageHttp m){
		try{
			String str = new String(m.marshall());
			URL url = new URL(String.format("%s/%s",_host,str));
			RpcCommunicator.instance().getLogger().debug(url.toString());
			HttpURLConnection urlcon = (HttpURLConnection)url.openConnection();
			urlcon.setRequestMethod(_method);
			urlcon.connect();         //鑾峰彇杩炴帴
			InputStream is = urlcon.getInputStream();
			BufferedReader buffer = new BufferedReader(new InputStreamReader(is));
			String xml = "";
			String line;
			while( (line = buffer.readLine())!=null){
				xml += line;
			} 
			xml = String.format("<NaviMSG msgcls=\"%s\" msg=\"%s\" type=\"%s\" calltype=\"%d\" sequence=\"%d\">",
						"Terminal","dummy","dummy",RpcMessage.RETURN,m.sequence) + xml;
			xml+= "</NaviMSG>";
			urlcon.disconnect();
			if(!decodeMsg(xml) ){
				RpcCommunicator.instance().getLogger().error("decode message http-get-result exception! data: ");
				RpcCommunicator.instance().getLogger().error(xml);
				return false;
			}
		}catch(Exception e){
			m.errcode = tce.RpcConsts.RPCERROR_SENDFAILED;
			RpcCommunicator.instance().getLogger().error("<1.>"+e.toString());
			return false;
		}
		return true;
	}
	
	private boolean sendPost2(RpcMessageHttp m){
		try{
			String str = new String(m.marshall());
			
			String url ;
			url = String.format("%s/%s",_host,m.msg);
			DefaultHttpClient httpClient = new DefaultHttpClient();  
			HttpPost post = new HttpPost(url);  
			List<BasicNameValuePair> postData = new ArrayList<BasicNameValuePair>();  
			if( m.http_params!=null){
				for (Map.Entry<String, String> entry : m.http_params.entrySet()) {  
					postData.add(new BasicNameValuePair(entry.getKey(), entry.getValue()));  
					System.out.print(entry.getValue());  
				}  
			}
			

			UrlEncodedFormEntity entity = new UrlEncodedFormEntity(postData,HTTP.UTF_8);//杩囨椂浜�  
			post.setEntity(entity);  
			
			if(m.http_head!=null){
				for (Map.Entry<String, String> entry : m.http_head.entrySet()) {  
					//postData.add(new BasicNameValuePair(entry.getKey(), entry.getValue()));  
					post.setHeader(new BasicHeader(entry.getKey(),entry.getValue()));  
				}  
			}
			
			
			 HttpResponse response = httpClient.execute(post); 
			 String result;
			 result = EntityUtils.toString(response.getEntity()); 
			
			String xml = result;
			int idx = xml.indexOf("?>");
			if(idx>=0){
				xml = xml.substring(idx+2);
			}
			
			xml = String.format("<NaviMSG msgcls=\"%s\" msg=\"%s\" type=\"%s\" calltype=\"%d\" sequence=\"%d\">",
						"Terminal","dummy","dummy",RpcMessage.RETURN,m.sequence) + xml;
			xml+= "</NaviMSG>";
			
			if(!decodeMsg(xml) ){
				RpcCommunicator.instance().getLogger().error("decode message http-post-result exception! data: ");
				RpcCommunicator.instance().getLogger().error(xml);
				return false;
			}
		}catch(Exception e){
			m.errcode = tce.RpcConsts.RPCERROR_SENDFAILED;
			RpcCommunicator.instance().getLogger().error("<1.>"+e.toString());
			return false;
		}
		return true;
	}
	
	private boolean sendPost(RpcMessageHttp m){
		try{
			String str = new String(m.marshall());
			str = str.substring(0, str.length()-1);
			URL url ;
			
			url = new URL(String.format("%s/%s/",_host,m.msg));
			
					
			RpcCommunicator.instance().getLogger().debug(url.toString());
			HttpURLConnection urlcon;
			
			urlcon = (HttpURLConnection)url.openConnection();
			urlcon.setRequestProperty("Content-Type","application/x-www-form-urlencoded");
			urlcon.setRequestProperty("IF-VERSION", "1");
			urlcon.setRequestMethod(_method);
			urlcon.setDoOutput(true);    
			urlcon.setDoInput(true);
			urlcon.setUseCaches(false);
			urlcon.setInstanceFollowRedirects(true);
			//urlcon.setRequestProperty("Content-Type","application/x-www-form-urlencoded");
			urlcon.setAllowUserInteraction(true);
			urlcon.connect();         //鑾峰彇杩炴帴
			//urlcon.setAllowUserInteraction(true); 
			DataOutputStream out = new DataOutputStream(urlcon.getOutputStream());
			
			out.writeBytes(str);
			out.flush();
			out.close();

			InputStream is = urlcon.getInputStream();
			
			BufferedReader buffer = new BufferedReader(new InputStreamReader(is));
			String xml = "";
			String line;
			while( (line = buffer.readLine())!=null){
				xml += line;
			} 
			
			int idx = xml.indexOf("?>");
			if(idx>=0){
				xml = xml.substring(idx+2);
			}
			
			xml = String.format("<NaviMSG msgcls=\"%s\" msg=\"%s\" type=\"%s\" calltype=\"%d\" sequence=\"%d\">",
						"Terminal","dummy","dummy",RpcMessage.RETURN,m.sequence) + xml;
			xml+= "</NaviMSG>";
			urlcon.disconnect();
			if(!decodeMsg(xml) ){
				RpcCommunicator.instance().getLogger().error("decode message http-post-result exception! data: ");
				RpcCommunicator.instance().getLogger().error(xml);
				return false;
			}
		}catch(Exception e){
			m.errcode = tce.RpcConsts.RPCERROR_SENDFAILED;
			RpcCommunicator.instance().getLogger().error("<1.>"+e.toString());
			return false;
		}
		return true;
	}
	
	@Override
	boolean  sendDetail(RpcMessage m){
		RpcMessageHttp httpmsg = (RpcMessageHttp)m; 
		if( _method == "GET"){
			return sendGet(httpmsg);
		}
		return sendPost2(httpmsg);
			
	}
	
	@Override
	public  boolean sendMessage(RpcMessage m){
		return sendDetail(m);
	}
	*/
}
