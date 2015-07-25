//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcProxyBase.h"
#import "RpcConnection.h"

@implementation RpcProxyBase

-(void) setToken:(NSString*)token{
    if( self.conn){
        if( self.conn.token!=token){
            [self.conn setToken:token];
            [self.conn close];
        }
    }
}

@end