package tce.netty;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import tce.RpcCommunicator;
import tce.RpcConnectionAcceptor;
import tce.RpcEndPoint;

import java.net.InetSocketAddress;
import java.util.UUID;

/**
 * Created by zhangbin on 16/9/6.
 */
public class RpcConnectionAcceptor_NettySocket extends RpcConnectionAcceptor {
    RpcEndPoint _ep;
    protected RpcConnectionAcceptor_NettySocket(){

    }

    public static RpcConnectionAcceptor_NettySocket create(RpcEndPoint ep){

        RpcConnectionAcceptor_NettySocket acceptor = new RpcConnectionAcceptor_NettySocket();
        acceptor._ep = ep ;

        return acceptor;
    }


    @Override
    public boolean open(){

        EventLoopGroup eg = new NioEventLoopGroup();
        ServerBootstrap sbt = new ServerBootstrap();
        try{
            sbt.group(eg);
            sbt.channel(NioServerSocketChannel.class);
            sbt.localAddress( new InetSocketAddress(_ep.host,_ep.port) );
            sbt.childHandler(new ChannelInitializer<SocketChannel>() {
                @Override
                protected void initChannel(SocketChannel socketChannel) throws Exception {
                    RpcConnection_NettySocket conn = new RpcConnection_NettySocket(socketChannel,RpcConnectionAcceptor_NettySocket.this);
                    String name = UUID.randomUUID().toString();
                    conn.setName(name);
                    conn.open();
                    addConnection( name,conn);
                }
            });

            ChannelFuture future = sbt.bind().sync();
//            future.channel().closeFuture().sync();
        }catch (Exception e ){
            RpcCommunicator.instance().getLogger().error(e.getMessage());
            eg.shutdownGracefully();
            return false;
        }
        return true;

    }


    @Override
    public void close(){}

}
