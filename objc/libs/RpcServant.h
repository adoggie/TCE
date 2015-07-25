//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

//#ifndef _RPC_SERVANT_H
//#define _RPC_SERVANT_H
//
@class RpcServantDelegate;

@interface RpcServant : NSObject

//@property (strong,nonatomic) RpcServantDelegate* delegate;
@property (strong,nonatomic) NSString*  name;
-(RpcServantDelegate*) getDelegate;
@end

//#endif
