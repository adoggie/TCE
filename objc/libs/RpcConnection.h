//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>
#import "RpcCommAdapter.h"
#import "RpcMessage.h"

//#ifndef _RPC_CONNECTION_H
//#define _RPC_CONNECTION_H

@interface RpcConnection : NSObject{
    @protected NSMutableDictionary*  _msglist;
    @protected BOOL _connected ;
}


@property  int          type;
@property   NSString*   token;

@property   (strong,nonatomic) RpcCommAdapter* adapter;


//+(RpcConnection*) create:(NSString*)host port:(int)port;
//-(void) setAdapter:(RpcCommAdapter *)adapter;
-(BOOL) connect;
-(void) open;
-(void) close;
-(void) run;

-(void) attachAdapter:(RpcCommAdapter*)adapter;
-(BOOL) isConnected;
-(BOOL) sendMessage:(RpcMessage*)msg;
-(BOOL) sendDetail:(RpcMessage*)msg;
-(void) doReturnMsg:(RpcMessage*)msgreturn;
-(void) dispatchMsg:(RpcMessage*) msg;


@end

//#endif
