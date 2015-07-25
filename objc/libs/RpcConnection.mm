//
// Created by zhang bin on 14-1-16.
// Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//
// To change the template use AppCode | Preferences | File Templates.
//


#import "RpcConnection.h"
#import "RpcAsyncCallBackBase.h"


@implementation RpcConnection {

}

-(id)init{
    self = [super init];
    self->_msglist = [NSMutableDictionary new];
    return self;
}

+(RpcConnection*) create:(NSString*)host port:(int)port{
    return nil;
}

//-(void) setAdapter:(RpcCommAdapter *)adapter{
//    [self setAdapter:adapter];
//}

-(BOOL) connect{
    return TRUE;
}

-(void) open{
    
}

-(void) close{
    
}

-(void) run{
    
}

-(void) attachAdapter:(RpcCommAdapter*)adapter{
    
}

-(BOOL) isConnected{
    return TRUE;
}

-(BOOL) sendMessage:(RpcMessage*)m{
    BOOL r = FALSE;
    @synchronized(self){
        if( (m.calltype&RpcMsgCallType_CALL)!=0 &&  (m.calltype&RpcMsgCallType_ONEWAY) ==0 ){
    //        @synchronized(self->_msglist){
                [self->_msglist setObject:m forKey:[NSNumber numberWithUnsignedInt:m.sequence]];
    //        }
        }
        
        r = [self sendDetail:m];
        if(!r){
            if((m.calltype&RpcMsgCallType_CALL)!=0 &&  (m.calltype&RpcMsgCallType_ONEWAY) ){
    //            @synchronized(self->_msglist){
                    [self->_msglist removeObjectForKey:[NSNumber numberWithUnsignedInt:m.sequence]];
    //            }
            }
        }
    }
    r = TRUE;
    return r;
}

-(BOOL) sendDetail:(RpcMessage*)m{
    return FALSE;
}

-(void) doReturnMsg:(RpcMessage*)m2{
    RpcMessage* m1 = nil;
    @synchronized(self->_msglist){
        m1 = [self->_msglist objectForKey:[NSNumber numberWithUnsignedInt:m2.sequence]];
        if(m1 !=nil){
            [self->_msglist removeObjectForKey:[NSNumber numberWithUnsignedInt:m2.sequence]];
        }
    }
    if( m1 !=nil){
        if( m1.async !=nil){
            [m1.async  callReturn:m1 m2:m2];
        }else{
            // nothing..
        }
    }
}

-(void) dispatchMsg:(RpcMessage*)m{
    if( (m.calltype&RpcMsgCallType_CALL)!=0){
        if( self.adapter!=nil){
            [self.adapter dispatchMsg:m];
        }
    }
    if( (m.calltype&RpcMsgCallType_RETURN)!=0){
        [self doReturnMsg:m];
    }
}


@end


