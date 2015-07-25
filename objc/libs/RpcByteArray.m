//
//  RpcByteArray.m
//  tce.project
//
//  Created by zhang bin on 14-1-19.
//  Copyright (c) 2014年 zhang bin. All rights reserved.
//

#import "RpcByteArray.h"
#import "RpcException.h"
#import "RpcConsts.h"

@implementation RpcByteArray{
    }

@synthesize bytes = _bytes;
@synthesize position = _position;


-(id)init{
    self = [super init];
    [self reset];
    return self;
}

//-(uint32_t) getSize{
//    return 0;
//}


+(id) initWithData:(const char*)data length:(uint32_t)length{
    RpcByteArray* bytearray= [RpcByteArray new];
    NSData* d = [NSData dataWithBytes:data length:length];
    [bytearray.bytes setData:d];
    return bytearray;
}

-(const char*) data{
    
    return self.bytes.bytes + self.position;
}

-(void) reset{
    [self setPosition:0];
    [self setBytes:[NSMutableData new]];
}

-(uint32_t) remain{
    return (uint32_t)[self.bytes length] - [self position];
}

-(void) writeChar:(int8_t)val{
    [self.bytes appendBytes:&val length:1];
}

-(void) writeByte:(uint8_t)val{
    int8_t i8 ;
    memcpy(&i8, &val, 1);
    [self writeChar:i8];
}

-(void) writeInt16:(int16_t)val{
    uint16_t ui16;
    memcpy(&ui16, &val, 2);
    [self writeUInt16:ui16];
}

-(void) writeUInt16:(uint16_t)val{
    val = NSSwapHostShortToBig(val);
    [self.bytes appendBytes:&val length:2];
}


-(void) writeInt32:(int32_t)val{
    uint32_t ui32;
    memcpy(&ui32,&val,4);
    [self writeUInt32:ui32];
}

-(void) writeUInt32:(uint32_t)val{
    val = NSSwapHostIntToBig(val);
    [self.bytes appendBytes:&val length:4];
}

-(void) writeInt64: (int64_t) val{
    uint64_t ui64;
    memcpy(&ui64, &val, sizeof(uint64_t));
    [self writeUInt64:ui64];
}
-(void) writeUInt64:(uint64_t) val{
    val = NSSwapHostLongToBig((unsigned long)val);
    [self.bytes appendBytes:&val length:sizeof(uint64_t)];
    
}

-(void) writeFloat:(float)val{
    uint32_t ui32;
    memcpy(&ui32,&val,sizeof(float));
    [self writeUInt32:ui32];
}

-(void) writeDouble:(double)val{
    uint64_t ui64;
    memcpy(&ui64,&val,sizeof(double));
    [self writeUInt64:ui64];
}


-(void) writeBytes:(const char*) bytes_ length:(uint32_t)length{
    [self writeUInt32:length];
    [self.bytes appendBytes:bytes_ length:length];
}

-(void) writeByteArray:(RpcByteArray*) array{
    [self writeUInt32:(uint32_t)[array.bytes length]];
    [self.bytes appendData:array.bytes];
}

-(void) writeData:(NSData*) data{
    [self writeUInt32:(uint32_t)[data length]];
    [self.bytes appendData:data];
}


-(void) writeString:(NSString*)val{
    uint32_t size = 0;
    const char* pstr = NULL;
    if( val!=nil){
        pstr = [val UTF8String];
        size = (uint32_t)strlen(pstr);
    }
    [self writeUInt32:size];
    if(size){
        [self.bytes appendBytes:pstr length:size];
    }
    
}

-(int8_t)   readChar {
    if( [self position] + 1 > [self.bytes length]){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    int8_t i8;
    [self.bytes getBytes:&i8 range:NSMakeRange(self.position, 1)];
    [self setPosition: self.position+1];
    return i8;
}

-(uint8_t)  readByte{
    int8_t i8 = [self readChar];
    return (uint8_t)i8;
}

-(int16_t)  readInt16{
    return (int16_t)[self readUInt16];
}

-(uint16_t) readUInt16{
    uint16_t ui16;
    if( [self position] + 2 > [self.bytes length]){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    [self.bytes getBytes:&ui16 range:NSMakeRange(self.position, 2)];
    ui16 = NSSwapBigShortToHost(ui16);
    [self setPosition: self.position+2];
    return ui16;
}

-(int32_t)  readInt32{
    return (int32_t)[self readUInt32];
}

-(uint32_t) readUInt32{
    uint32_t ui32;
    if( [self position] + 4 > [self.bytes length]){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    [self.bytes getBytes:&ui32 range:NSMakeRange(self.position, 4)];
    ui32 = NSSwapBigIntToHost(ui32);
    [self setPosition: self.position+4];
    return ui32;
}

-(int64_t)  readInt64{
    return (int64_t)[self readUInt64];
}

-(uint64_t) readUInt64{
    uint64_t ui64;
    if( [self position] + 8 > [self.bytes length]){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    [self.bytes getBytes:&ui64 range:NSMakeRange(self.position, 8)];
    ui64 = NSSwapBigLongToHost((unsigned long)ui64);
    [self setPosition: self.position+8];
    return ui64;
}

-(float)    readFloat{
    uint32_t ui32;
    ui32 = [self readUInt32];
    float   r32;
    memcpy(&r32,&ui32,4);
    return r32;
}

-(double)   readDouble{
    uint64_t ui64 ;
    ui64 = [self readUInt64];
    double r64;
    memcpy(&r64,&ui64,8);
    return r64;
}

-(NSString*)    readString{
    uint32_t size ;
    size = [self readUInt32];
    if( size == 0){
        return @"";
    }
    if( self.position + size > self.bytes.length){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    const char * pstr = [self.bytes bytes] + self.position;
    NSString* result = [[NSString alloc] initWithBytes:pstr length:size encoding:NSUTF8StringEncoding];
    [self setPosition:self.position + size];
    return result;
}

-(NSData*) readDataWithSize:(uint32_t)size{
    if( self.position + size > self.bytes.length){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    const char * pstr = [self.bytes bytes] + self.position;
    NSData* result = [NSData dataWithBytes:pstr length:size];
    [self setPosition:self.position + size];
//    result length
    
    return result;
}


-(NSData*) readData{
    uint32_t size = [self readUInt32];
    if( self.position + size > self.bytes.length){
        [RpcException raise:RPCERROR_DATA_INSUFFICIENT message:nil];
    }
    NSData* data;
    data = [self readDataWithSize:size];
    return data;
}


@end
