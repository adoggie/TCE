//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>


@class  RpcMessage;

@interface RpcAsyncCallBackBase : NSObject{
    
}



@property id delta;

@property id onSucc;
@property id onError;


-(void) callReturn:(RpcMessage*)m1 m2:(RpcMessage*)m2;
//-(void) onError:(int)errcode;

@end