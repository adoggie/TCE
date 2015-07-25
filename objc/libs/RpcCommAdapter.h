//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

@class RpcConnection;
@class RpcMessage;
@class RpcServant;

@interface RpcCommAdapter : NSObject{
    NSMutableDictionary*     _servants;
    NSMutableArray*     _conns;
}

@property NSString* ID;
@property NSString* host;
@property int   port;

+(RpcCommAdapter*) initWithId:(NSString*) _id;

-(BOOL) open:(NSString*) host port:(int)port;
-(void) close;
-(void) addServant:(RpcServant*)servant;
-(void) join;
-(void) dispatchMsg:(RpcMessage*)msg;
-(void) addConnection:(RpcConnection*)conn;
-(void) removeConnection:(RpcConnection*)conn;

@end