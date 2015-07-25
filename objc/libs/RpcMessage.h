//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import <Foundation/Foundation.h>

//#ifndef _RPC_MESSAGE_H
//#define _RPC_MESSAGE_H

//#import "RpcExtraData.h"
//#import "RpcProxyBase.h"
//#import "RpcAsyncCallBackBase.h"
//#import "RpcConnection.h"
#import "RpcConsts.h"
#import "RpcByteArray.h"
#import "RpcExtraData.h"

@class RpcConnection;
@class RpcExtraData;
@class RpcAsyncCallBackBase;
@class RpcProxyBase;


enum _tagRpcMessageCallType{
	RpcMsgCallType_CALL    = 0x01,
	RpcMsgCallType_RETURN  = 0x02,
	RpcMsgCallType_TWOWAY  = 0x10,
	RpcMsgCallType_ONEWAY  = 0x20,
	RpcMsgCallType_ASYNC   = 0x40
};

@interface RpcMessage : NSObject{
//    uint32_t    _sequence;
}
@property (strong, nonatomic) RpcExtraData * extra;
@property (strong) RpcProxyBase *   proxy;
@property (strong)  RpcAsyncCallBackBase * async;
@property (strong)  RpcMessage *    callmsg;
@property (strong)  RpcConnection * conn;
@property       id      cookie;

//@property void (^onResult)(void);

@property uint8_t       type;
@property uint32_t      sequence;
@property uint8_t       calltype;
@property uint16_t      ifidx;
@property uint16_t      opidx;
@property int           errcode;
@property uint8_t       paramsize;
@property uint16_t      call_id;
@property    RpcByteArray*    content;

-(id) initWithCallType:(int) calltype;
-(void)  marshall:(RpcByteArray*)bytearray;
+(id) unmarshall:(RpcByteArray*)bytearray;


@end

//#endif
