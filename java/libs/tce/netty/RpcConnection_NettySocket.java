package tce.netty;


import io.netty.bootstrap.Bootstrap;
import io.netty.channel.*;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;

import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.channel.socket.nio.NioSocketChannel;
import tce.RpcCommunicator;
import tce.RpcConnectionAcceptor;
import tce.RpcConnection_Socket;

/**
 * Created by zhangbin on 16/9/6.
 */


public class RpcConnection_NettySocket extends RpcConnection_Socket {

    SocketChannel _channel = null;
    RpcConnection_Socket.MessageReactor _reactor ;

    RpcConnection_NettySocket(String host, int port ){
        super(host,port );
    }


    RpcConnection_NettySocket(SocketChannel channel, RpcConnectionAcceptor_NettySocket acceptor){
        _channel = channel;
        setAcceptor(acceptor);

    }

    protected  void setChannel(SocketChannel channel){
        _channel = channel;
    }

    @Override
    public boolean open(){
        try {
            _reactor = new RpcConnection_Socket.MessageReactor(this);

            _channel.pipeline().addLast(new ChannelInboundHandlerAdapter() {
                public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
                    ByteBuf buf = (ByteBuf) msg;
                    byte[] bytes = new byte[buf.readableBytes()];
                    buf.readBytes(bytes);
                    RpcConnection_NettySocket conn = RpcConnection_NettySocket.this;
                    conn._reactor.enqueue(bytes,bytes.length);
                }

                @Override
                public void handlerRemoved(ChannelHandlerContext ctx) throws Exception {
                    RpcConnection_NettySocket conn = RpcConnection_NettySocket.this;
                    conn.onDisconnected();
                }

                @Override
                public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause)
                        throws Exception {
//                   cause.toString()
                }

            });
        }catch (Exception e){
            RpcCommunicator.instance().getLogger().error(e.getMessage());
            return false;
        }
        return true;
    }

    @Override
    protected  void onDisconnected(){
        RpcConnectionAcceptor acceptor = (RpcConnectionAcceptor)getAcceptor();
        if( acceptor != null){
            acceptor.removeConnection(getName());
        }
    }

    @Override
    public void close(){

    }

    @Override
    protected  boolean sendBytes(byte[] bytes) {
        ByteBuf buf = Unpooled.copiedBuffer(bytes);
        _channel.writeAndFlush( buf );
        return true;
    }

    @Override
    protected void join(){


    }

    @Override
    public  boolean connect(){
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(workerGroup);
            b.channel(NioSocketChannel.class);
            b.option(ChannelOption.SO_KEEPALIVE, true);
            b.handler(new ChannelInitializer<SocketChannel>() {
                @Override
                public void initChannel(SocketChannel channel) throws Exception {
                    RpcConnection_NettySocket.this.setChannel(channel);
                    RpcConnection_NettySocket.this.open();
                }
            });
            ChannelFuture f = b.connect(_host, _port).sync();
//            f.channel().closeFuture().sync();
        } catch (Exception e){
            RpcCommunicator.instance().getLogger().error( e.getMessage());
            workerGroup.shutdownGracefully();
            return false;
        }
        return true;
    }



}
