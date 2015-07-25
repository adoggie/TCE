//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

@class RpcMessage;
@class RpcCommAdapter;
@class RpcConnection;
@class RpcLogger;
@class RpcProxyBase;

@interface RpcCommunicator : NSObject{
    NSMutableDictionary* _adapters;
    int _sequence;
    
    
}
@property (strong,nonatomic) RpcLogger* logger;

+(RpcCommunicator*) instance;
-(BOOL) initialize;
-(int) nextSequence;
-(void) waitForShutdown;
-(void) shutdown;
-(RpcCommAdapter*) createAdapterWithProxy:(NSString*) _id proxy:(RpcProxyBase*)proxy;
-(void) addAdapter:(RpcCommAdapter*)adapter;
-(RpcCommAdapter*) createAdapter:(NSString*)_id;
//-(RpcConnection*) createConnection:(int)type host:(NSString*) host port:(int)port;
-(RpcConnection*) createConnection:(NSString*) host port:(int)port;


@end