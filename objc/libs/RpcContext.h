//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

@class RpcMessage;

@interface RpcContext : NSObject

@property (strong,nonatomic) RpcMessage* msg;

@end