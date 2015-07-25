//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

@class RpcCommAdapter;
@class RpcMessage;
@class RpcServant;

@interface RpcServantDelegate : NSObject

@property (nonatomic)           int ifidx; //接口索引
@property (strong,nonatomic)    RpcCommAdapter* adapter;
//@property                       RpcServant* servant;
-(BOOL) invoke:(RpcMessage*) msg;

@end