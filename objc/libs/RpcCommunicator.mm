//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcCommunicator.h"
#import "RpcMessage.h"
#import "RpcProxyBase.h"
#import "RpcConnection.h"
#import "RpcCommAdapter.h"
#import "RpcConnectionTcpStream.h"


@implementation RpcCommunicator {

}

+(RpcCommunicator*) instance{
    static RpcCommunicator* communicator = nil;
    static dispatch_once_t oncetoken;
    dispatch_once(&oncetoken,^{
        communicator = [RpcCommunicator new];
    });
    return communicator;
}

-(BOOL) initialize{
    return TRUE;
}

-(int) nextSequence{
    @synchronized(self){
        if( self->_sequence == 0xffffff){
            self->_sequence = 0;
        }else{
            self->_sequence+=1;
        }
    }
    return self->_sequence;
}

-(void) waitForShutdown{
    
}

-(void) shutdown{
    
}

-(RpcCommAdapter*) createAdapterWithProxy:(NSString*) _id proxy:(RpcProxyBase*)proxy{
    RpcCommAdapter* adapter = nil;
    adapter = [RpcCommAdapter initWithId:_id];
    [proxy.conn setAdapter:adapter];
    [self addAdapter:adapter];
    return adapter;
}

-(void) addAdapter:(RpcCommAdapter*)adapter{
    [self->_adapters setValue:adapter forKey:[adapter ID]];
    
}

-(RpcCommAdapter*) createAdapter:(NSString*)_id{
    RpcCommAdapter* adapter = [RpcCommAdapter initWithId:_id];
    return adapter;
}

-(RpcConnection*) createConnection:(NSString*) host port:(int)port{
    return [RpcConnectionTcpStream create:host port:port];
}


@end




