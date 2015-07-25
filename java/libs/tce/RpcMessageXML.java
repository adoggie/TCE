package tce;
import tce.RpcMessage;
import tce.RpcCommunicator;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
//import org.w3c.dom.Node;
import java.io.*;
//import java.util.*;
import java.util.Map;


// msgcls.msg 闁活枎鎷烽柛鎺戞婢癸拷闁硅揪鎷穖sgcls闁告粌顔卻g闁挎冻鎷穖sgcls濞达絾绮堢拹鐔煎箳閵夈儱缍撻柛姘Ф琚�, msg 濞达絾绮堢拹鐔煎箳閵夈儱缍撻柛鎰噽濞堟垿宕欓懞銉︽闁告艾绉惰ⅷ

public class RpcMessageXML  extends RpcMessage{
	public String xml =""; //
	public Map<String, String> http_params = null ;
	public Map<String,String> http_head = null;
	public String msg;	
	public String msgcls; 
	public Element parentNode;
	
	public RpcMessageXML(int calltype_){
		super(calltype_);
	}
	
	public static RpcMessage unmarshall(byte[] d){
		RpcMessageXML m;

		try{
//			RpcCommunicator.instance().getLogger().error( new String(d));
			
			
			DocumentBuilderFactory factory =DocumentBuilderFactory.newInstance();
	        DocumentBuilder builder =factory.newDocumentBuilder();
	        ByteArrayInputStream is = new ByteArrayInputStream(d);  
	        Document dom = builder.parse(is);
	        Element root = dom.getDocumentElement();
	        //System.out.println(root.getTagName());
	        if( root.getTagName().equals("NaviMSG") == false){
	        	return null;
	        }
	        String cls_msg  = root.getAttribute("type"); 
	       
	        String[] pair;
	        pair = cls_msg.split("\\.");
	        if(pair.length<2){
	        	cls_msg = "Terminal."+cls_msg; // 闁煎浜滅换渚�礉閻樿京鐟愬娑欘焾椤撳鎯冮崟顒佹嫳闁革妇娅塭rminal闁规亽鍎辫ぐ娑氱尵鐠囨彃鐒�	        }
	        }
	        pair = cls_msg.split("\\.");
	       /* if( pair.length!=2){
	        	RpcCommunicator.instance().getLogger().error(String.format("invalid msg cls: %s",cls_msg));
	        	return null;
	        }*/
	        int calltype;
	        calltype = Integer.valueOf( root.getAttribute("calltype").trim()).intValue();
	        int seq;
	        seq = Integer.valueOf(root.getAttribute("sequence").trim()).intValue();
	        m = new RpcMessageXML(calltype);
	        m.sequence = seq;
	        m.msg = pair[1];
	        m.msgcls = pair[0];
	        m.parentNode = root;
	       
		}catch(Exception e){
			
			RpcCommunicator.instance().getLogger().error( e.getMessage());
			m = null;
		}
		return m;
	}
	
	@Override
	public byte[] marshall(){
		String packet;
		packet = String.format("<NaviMSG msgcls=\"%s\" msg=\"%s\" type=\"%s\" calltype=\"%d\" sequence=\"%d\">",
					msgcls,msg,msg,this.calltype,this.sequence);
		packet+= xml;
		packet+= "</NaviMSG>";
		RpcCommunicator.instance().getLogger().debug( String.format("(marshalling) >> %s \n",packet) );
		
		return packet.getBytes();
	}
}