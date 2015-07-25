//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcMessage.h"
#import "RpcCommunicator.h"

@implementation RpcMessage {

}

//@synthesize extra;
//@synthesize proxy;
//@synthesize asyncCB;
//@synthesize callmsg;
//@synthesize conn;
//@synthesize sequence = _sequence;

//-(RpcMessage *) init{
//	self = [super init];
//	if(self){
//
//	}
//	return self;
//}

-(id)init{
    self = [super init];
    [self setExtra:[RpcExtraData new]];
    self->_sequence = [[RpcCommunicator instance] nextSequence];
    return self;
    
}

-(id) initWithCallType:(int) calltype{
    self = [self init];
    if(self){
        [self setCalltype:calltype];
        if ( (self.calltype & RpcMsgCallType_CALL) !=0) {
            
        }
    }
//    dispatch_async(<#dispatch_queue_t queue#>, <#^(void)block#>)
    return self;
}

-(void) marshall:(RpcByteArray*)bytearray{
    [bytearray writeByte: MSGTYPE_RPC];
    [bytearray writeUInt32: [self sequence]];
    [bytearray writeByte:[self calltype]];
    [bytearray writeUInt16: [ self ifidx]];
    [bytearray writeUInt16:[ self opidx]];
    [bytearray writeInt32:[ self errcode]];
    [bytearray writeByte:[self paramsize]];
    [bytearray writeUInt16:[self call_id]];
    [self.extra marshall:bytearray];
    if(self.content !=nil){
//        [bytearray writeData:[self.content bytes]];
        [bytearray.bytes appendData:self.content.bytes];
    }
}

+(id) unmarshall:(RpcByteArray*)bytearray{
    RpcMessage* msg = nil;
    @try {
        msg = [RpcMessage new];
        [msg setType:[bytearray readByte]];
        [msg setSequence:[bytearray readUInt32]];
        [msg setCalltype:[bytearray readByte]];
        [msg setIfidx:[bytearray readUInt16]];
        [msg setOpidx:[bytearray readUInt16]];
        [msg setErrcode:[bytearray readInt32]];
        [msg setParamsize:[bytearray readByte]];
        [msg setCall_id:[bytearray readUInt16]];
        [msg.extra unmarshall:bytearray];
        [msg setContent:[RpcByteArray initWithData:[bytearray data] length: [bytearray remain]]];
    }
    @catch (NSException *exception) {
        NSLog(@"%@",exception.description);
        msg = nil;
    }
    @finally {
        return msg;
    }
    
}


@end