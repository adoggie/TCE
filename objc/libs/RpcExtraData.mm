//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcExtraData.h"


@implementation RpcExtraData {

}

-(id)init{
    self = [super init];
    self->_properties = [NSMutableDictionary new];
    return self;
}


/**
    序列化本地对象到序列化对象
 */
-(void) marshall:(RpcByteArray*)bytearray{
    NSArray* array = [self.properties allKeys];
    size_t size = (uint32_t) [self.properties count] ;
    [bytearray writeUInt32:(uint32_t)size];
    for(int n=0;n< [self.properties count];n++){
        NSString* key = [array objectAtIndex:n];
        NSString* value = [self.properties objectForKey:key];
        [bytearray writeString:key];
        [bytearray writeString:value];
    }

}

//从字节缓冲区生成extradata对象
-(void) unmarshall:(RpcByteArray*)bytearray{
    RpcExtraData * extra = self;
//    extra = [RpcExtraData new];
    uint32_t size = [bytearray readUInt32];
    for(uint32_t n = 0;n < size ;n++){
        NSString* key = [bytearray readString];
        NSString* value = [bytearray readString];
        [[extra properties] setObject:value forKey:key];
    }
}


@end