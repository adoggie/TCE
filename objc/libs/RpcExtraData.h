//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

#import "RpcByteArray.h"

@interface RpcExtraData : NSObject

@property (nonatomic,strong) NSMutableDictionary* properties;

-(void) marshall:(RpcByteArray*)bytearray;
-(void) unmarshall:(RpcByteArray*)bytearray;

@end