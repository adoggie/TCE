//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

#import "RpcConnection.h"

@interface RpcConnectionTcpStream : RpcConnection<NSStreamDelegate>

@property NSString*     host;
@property int           port;
@property   NSInputStream* instream;
@property   NSOutputStream* outstream;


+(RpcConnection*) create:(NSString*)host port:(int)port;

@end