//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>


@interface RpcException : NSException


@property (strong) NSString*    msg;
@property  (assign) int         errcode;

+(id) initWithError:(int)errcode message:(NSString*)msg;
-(NSString*) what;

+(void) raise:(int)errcode message:(NSString*)msg;

@end