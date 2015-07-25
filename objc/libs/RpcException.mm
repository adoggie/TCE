//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcException.h"


@implementation RpcException {
   
}

@synthesize errcode;
@synthesize msg;

+(id) initWithError:(int)errcode message:(NSString*)msg{
    RpcException* exp = [RpcException alloc];
    exp = [exp initWithName:nil reason:nil userInfo:nil];
    exp.errcode = errcode;
    [exp setMsg: msg];
    return exp;
}

-(NSString*) what{
    return [self msg];
}


+(void) raise:(int)errcode message:(NSString*)msg{
    RpcException* exp = [RpcException initWithError:errcode message:msg];
    [exp raise];
}

@end