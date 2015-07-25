package tce;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.TrustManagerFactory;
import java.net.Socket;
import java.security.KeyStore;

/**
 * Created by scott on 6/20/14.
 */
public class RpcConnection_SocketSSL extends RpcConnection_Socket {

	public RpcConnection_SocketSSL(String host, int port) {
		super(host, port);
	}

//	private class SSLEnviroment{
//		public final static SSLEnviroment instance = null;
//		if( SSLEnviroment.)
//	}
	@Override
	protected Socket newSocket() {
//		return super.newSocket();
		Socket sock = null;
		try {
			//取得SSL的SSLContext实例
//			SSLContext sslContext = SSLContext.getInstance(CLIENT_AGREEMENT);
			SSLContext sslContext = SSLContext.getDefault();

			 //取得KeyManagerFactory和TrustManagerFactory的X509密钥管理器实例
//			KeyManagerFactory keyManager = KeyManagerFactory.getInstance(CLIENT_KEY_MANAGER);
//			TrustManagerFactory trustManager = TrustManagerFactory.getInstance(CLIENT_TRUST_MANAGER);
			//取得BKS密库实例
//			KeyStore kks= KeyStore.getInstance(CLIENT_KEY_KEYSTORE);
//			KeyStore tks = KeyStore.getInstance(CLIENT_TRUST_KEYSTORE);
			//加客户端载证书和私钥,通过读取资源文件的方式读取密钥和信任证书
//			kks.load(getBaseContext()
//			        .getResources()
//			        .openRawResource(R.drawable.kclient),CLIENT_KET_PASSWORD.toCharArray());
//			tks.load(getBaseContext()
//			        .getResources()
//			        .openRawResource(R.drawable.lt_client),CLIENT_TRUST_PASSWORD.toCharArray());
			//初始化密钥管理器
//			keyManager.init(kks,CLIENT_KET_PASSWORD.toCharArray());
//			trustManager.init(tks);
//			//初始化SSLContext
//			sslContext.init(keyManager.getKeyManagers(),trustManager.getTrustManagers(),null);
			//生成SSLSocket
			sock = (SSLSocket) sslContext.getSocketFactory().createSocket();
		} catch (Exception e) {
//			tag.e("MySSLSocket",e.getMessage());
			System.out.println(e.toString());

		}
		return sock;

	}
}
