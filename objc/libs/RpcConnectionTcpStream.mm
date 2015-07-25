//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <unistd.h>
#import <sys/socket.h>
#import <netinet/in.h>
#import <arpa/inet.h>
#import "RpcConnectionTcpStream.h"
#import "RpcAsyncCallBackBase.h"
#import "RpcMessage.h"


@implementation RpcConnectionTcpStream {
    CFSocketRef _sock;
    uint32_t    _sentPkgNum;
    dispatch_queue_t _serialQ;
}

+(RpcConnection*) create:(NSString*)host port:(int)port{
    RpcConnectionTcpStream * conn = [RpcConnectionTcpStream new];
    conn.host = host;
    conn.port = port;
    conn->_serialQ = dispatch_queue_create("q.sendmsg", DISPATCH_QUEUE_SERIAL);
    return conn;
}

/*
-(void)stream:(NSStream *)aStream handleEvent:(NSStreamEvent)eventCode{
    
    switch(eventCode){
        case NSStreamEventOpenCompleted:
            NSLog(@"stream openned!");
            break;
        case NSStreamEventEndEncountered:
            NSLog(@"end encountered"); // socket closed
            [self.instream close];
            [self.instream removeFromRunLoop: [ NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
            //            [self.instream release];
            
            break;
        case NSStreamEventErrorOccurred:
            NSLog(@"error occurred!"); // socket connect failed!
            break;
        case NSStreamEventHasSpaceAvailable:
            NSLog(@"outstream is available..");
            break;
        case NSStreamEventHasBytesAvailable:{
            NSInteger rb ;
            uint8_t data[1024];
            //            NSInteger len ;
            rb = [self.instream read:data maxLength:  sizeof(data)];
            NSLog(@"%ld bytes recieved!",(long)rb);
        }
    }
}
 */

-(BOOL) connect{
    if( self->_connected){
        return TRUE;
    }
    NSLog(@"connect: %d",self->_connected);
    NSLog(@"try connect server...");
//    sleep(2);
    
    CFSocketContext sctx;
    memset(&sctx,0,sizeof(sctx));
    sctx.info =(__bridge void*) self;
    self->_sock = CFSocketCreate(kCFAllocatorDefault, PF_INET, SOCK_STREAM, IPPROTO_TCP, 0, NULL, &sctx);
    if(self->_sock != nil){
        struct sockaddr_in addr4;   // IPV4
        memset(&addr4, 0, sizeof(addr4));
        addr4.sin_len = sizeof(addr4);
        addr4.sin_family = AF_INET;
        addr4.sin_port = htons(self->_port);
        addr4.sin_addr.s_addr = inet_addr([self->_host UTF8String]);  // 把字符串的地址转换为机器可识别的网络地址
        
        // 把sockaddr_in结构体中的地址转换为Data
        CFDataRef address = CFDataCreate(kCFAllocatorDefault, (UInt8 *)&addr4, sizeof(addr4));
        CFSocketError serr = CFSocketConnectToAddress(self->_sock, // 连接的socket
                                 address, // CFDataRef类型的包含上面socket的远程地址的对象
                                 5.0  // 连接超时时间，如果为负，则不尝试连接，而是把连接放在后台进行，如果_socket消息类型为kCFSocketConnectCallBack，将会在连接成功或失败的时候在后台触发回调函数
                                 );
//        CFRunLoopRef cRunRef = CFRunLoopGetCurrent();    // 获取当前线程的循环
//        // 创建一个循环，但并没有真正加如到循环中，需要调用CFRunLoopAddSource
//        CFRunLoopSourceRef sourceRef = CFSocketCreateRunLoopSource(kCFAllocatorDefault, self->_sock, 0);
//        CFRunLoopAddSource(cRunRef, // 运行循环
//                           sourceRef,  // 增加的运行循环源, 它会被retain一次
//                           kCFRunLoopCommonModes  // 增加的运行循环源的模式
//                           );
//        CFRelease(sourceRef);
        
        if( serr == kCFSocketSuccess){
            self->_connected = TRUE;
//            [self sendToken];
            [self performSelectorInBackground:@selector(_readData) withObject:nil];
        }
        
    }
    
    return self->_connected;
}

-(void) sendToken{
    if( self.token !=nil){
        
    }
}

-(void)_readData{
    char buffer[1024];
//    NSLog(@"readData in Thread:%@",[NSThread currentThread]);
    
    NSMutableData * data = [NSMutableData new];
    while ( true){
        ssize_t len = recv(CFSocketGetNative(self->_sock),buffer, sizeof(buffer), 0);
        if(len <=0 ){
            break;
        }
        [data appendBytes:buffer length:len];
        NSMutableArray* blocks = [NSMutableArray new];
        size_t size = (size_t) data.length;
        int r = [self parseData:(const char*)data.mutableBytes size:&size blocks:blocks];
        if( r == -1){
            NSLog(@"error: parseData failed!");
            close(CFSocketGetNative(self->_sock));
//            [self doClose];
            break;
        }else if( r == 0){ // need more
//            continue;
        }
        [data replaceBytesInRange:NSMakeRange( 0,(data.length - size)) withBytes:NULL length:0]; //删除已解释的数据
        for( RpcByteArray* block in blocks){
            RpcMessage* msg = [RpcMessage unmarshall:block];
            if( msg!=nil){
                msg.conn = self;
                @try {
                    [self dispatchMsg:msg];
                }
                @catch (NSException *exception) {
                    NSLog(@"error: dispatchMsg()  detail:%@",exception.description);
                }
                @finally {
                    
                }
                
            }else{
                NSLog(@"error: RpcMessage unmarshall failed!");
                break;
            }
        }
    }
    // 线程准备推出
    [self onDisconnected];
}

-(void) onConnected{
    @synchronized(self){
        self->_sentPkgNum = 0;
        self->_connected = TRUE;
    }
}

-(void) onDisconnected{
    @synchronized(self){
        self->_connected = FALSE;
        self->_sock = nil;
        self->_sentPkgNum = 0 ;
    }
}



#define READ_BUFFSIZE  1024*5
#define WRITE_BUFFSIZE READ_BUFFSIZE
#define PACKET_HDRSIZE 14
#define MAX_PACKET_SIZE (1024*1024*2) //最大1MB一个数据包


#define META_PACKET_HDR_SIZE    14
#define PACKET_META_MAGIC       0xEFD2BB99
#define VERSION                 0x00000100
//#define MAX_PACKET_SIZE = 1024*1024*1

/// >=1 - ok(consumed   bytes) , 0 - need more, -1: data dirty
-(int) parseData:(const char *)d size:(size_t*)dsize blocks:(NSMutableArray*)blocks{

//	const char  * p1;
//	p1 = d;
//    
    
	while( *dsize  > 0){
		if( *dsize < PACKET_HDRSIZE){
			return 0;
		}
        RpcByteArray* bytes= [RpcByteArray initWithData:d length:PACKET_HDRSIZE];
		uint32_t magic;
		uint32_t size;
		uint8_t compress,encrypt;
		uint32_t version;
        magic = [ bytes readUInt32];
        size = [bytes readUInt32];
        compress = [bytes readByte];
        encrypt = [bytes readByte];
        version = [bytes readUInt32];
        
		if( 0xEFD2BB99!= magic){
			return -1;
		}

		if( (*dsize) > MAX_PACKET_SIZE){
			return -1;
		}
		if(size<=10){
			return -1; // dirty
		}
		if( *dsize < size+4 ){
			return 0;
		}
        RpcByteArray* block =[RpcByteArray initWithData:d+PACKET_HDRSIZE length:size-PACKET_HDRSIZE+4];
        [blocks addObject:block];
		d += size+4;
		(*dsize) -= size+4;
	}
	return 1;
}


/*
-(BOOL) _connect{
    CFReadStreamRef readstream;
    CFWriteStreamRef writestream;
    
    CFStreamCreatePairWithSocketToHost(NULL, (__bridge CFStringRef)self.host, self.port, &readstream, &writestream);
    self.instream  = (__bridge_transfer NSInputStream*)readstream;
    self.outstream = (__bridge_transfer NSOutputStream*)writestream;
    
    [self.instream setDelegate:self ];
    
    [self.instream scheduleInRunLoop: [NSRunLoop currentRunLoop]  forMode:NSDefaultRunLoopMode];
    
    [self.outstream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [self.instream open];
    [self.outstream open];
    
    return TRUE;
}
 
 */

-(void) open{
    
}

-(void) close{
    @synchronized(self){
        if( self->_sock !=nil){
            int fd = CFSocketGetNative(self->_sock);
            close(fd);
        }
    }
    
}



-(BOOL) sendMessage:(RpcMessage*)msg{
    return [super sendMessage:msg];
}

-(ssize_t) sendall:(int)fd data:(const char*)data datasize:(size_t)datasize{
    const char* p = (const char*)data;
    const char* begin = p;
    const char* end = begin + datasize;
    while(p < end){
        size_t size = end - p;
        ssize_t r = send(fd, p, size, 0);
        if( r <= 0){
            close(fd);
            return -1;
        }
        p+=r;
    }
    return datasize;
}

-(void) _sendData:(RpcMessage*)msg{
    
//    NSLog(@"_sendData in Thread:%@",[NSThread currentThread]);
    
    if(self->_sentPkgNum == 0){
        if(self.token !=nil){
            [msg.extra.properties setObject:self.token forKey:@"__token__"];
        }
    }
    
    //META packet encapsulated
    RpcByteArray* bar = [RpcByteArray new];
    [msg marshall:bar];
    RpcByteArray* body = [RpcByteArray new];
    
    [body writeUInt32:PACKET_META_MAGIC];
    [body writeUInt32:(uint32_t)(bar.bytes.length+ META_PACKET_HDR_SIZE -4) ];
    [body writeByte:COMPRESS_NONE];
    [body writeByte:ENCRYPT_NONE];
    [body writeUInt32:VERSION];
    [body.bytes appendData:bar.bytes];

    int fd = CFSocketGetNative(self->_sock);
    const char* p = (const char*)[body.bytes bytes];
    
    [self sendall:fd data:p datasize:(size_t)body.bytes.length];
    self->_sentPkgNum += 1;
    if(self->_sentPkgNum >= 0xff000000){
        self->_sentPkgNum = 1;
    }
}

-(BOOL) sendDetail: ( RpcMessage*) msg{
//    dispatch_queue_t serialQ = dispatch_queue_create("q.sendmsg", DISPATCH_QUEUE_SERIAL);
//    dispatch_queue_t q = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);

    dispatch_async(self->_serialQ, ^{
        
        [self connect];
        if(self->_connected){
            [self _sendData:msg];
        }else{  //无法建立连接则直接丢弃此消息，并以onError通知给调用者
            if (msg.async!=nil && msg.async.onError!=nil){
                void (^fx_error)(int error,RpcProxyBase* proxy,id cookie) = msg.async.onError;
                fx_error(RPCERROR_CONNECT_UNREACHABLE,msg.proxy,msg.cookie);
            }
        }
    });
//    dispatch_release(serialQ);

    return TRUE;
}

@end