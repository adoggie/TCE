//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcCommAdapter.h"
#import "RpcServant.h"
#import "RpcServantDelegate.h"
#import "RpcConnection.h"
#import "RpcMessage.h"
#import "RpcConsts.h"


@implementation RpcCommAdapter {

}

-(id)init{
    self = [super init];
    self->_conns = [NSMutableArray new];
    self->_servants = [NSMutableDictionary new];
    return self;
}

+(RpcCommAdapter*) initWithId:(NSString*) _id{
    RpcCommAdapter* adapter = [RpcCommAdapter new];
    [adapter setID:_id];
    return adapter;
}

-(BOOL) open:(NSString*) host port:(int)port{
    self.host = host;
    self.port = port;
    return TRUE;
}

-(void) close{
    
}

-(void) addServant:(RpcServant*)servant{
    @synchronized(self){
        int ifidx = [[servant getDelegate] ifidx];
        if([self->_servants objectForKey: [NSNumber numberWithInt: ifidx] ] != nil){
            return ;
        }
        [self->_servants setObject:servant forKey:[NSNumber numberWithInt: ifidx]];
    }
}

-(void) join{
    
}

-(void) dispatchMsg:(RpcMessage*)msg{
    RpcServantDelegate * delegate = nil;
    RpcServant * servant = nil;
    if( msg.calltype & RpcMsgCallType_CALL){
        @synchronized(self->_servants){
            NSNumber* ifidx = [NSNumber numberWithInt: msg.ifidx ];
            servant = [self->_servants objectForKey: ifidx];
            if(servant!=nil){
                delegate = [servant getDelegate];
            }
            if( delegate == nil){
                [self doError:RPCERROR_INTERFACE_NOTFOUND msg:msg];
                return;
            }
        }
        @try {
            if( delegate !=nil){
                [delegate invoke:msg];
            }
        }
        @catch (NSException *exception) {
            NSLog(@"%@",exception.description);
        }
        @finally {
            
        }
    }
}

-(void) addConnection:(RpcConnection*)conn{
    @synchronized(self){
        if( [ self->_conns containsObject:conn] ){
            return ;
        }
        [ self->_conns addObject:conn];
        [conn setAdapter:self];
    }
    
}

-(void) removeConnection:(RpcConnection*)conn{
    @synchronized(self){
        if( [self->_conns containsObject:conn]){
            [self->_conns removeObject:conn ];
        }
    }
}

-(void) doError:(RpcErrorCodeType_t) errcode msg:(RpcMessage*)msg{
    
}


@end