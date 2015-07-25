//
//  RpcByteArray.h
//  tce.project
//
//  Created by zhang bin on 14-1-19.
//  Copyright (c) 2014年 zhang bin. All rights reserved.
//

#import <Foundation/Foundation.h>
//#import "tce.h"

@interface RpcByteArray : NSObject{
//    NSMutableData* _bytes;
//    uint32_t    _position;

}

//@property (

@property NSMutableData* bytes;
@property     uint32_t position;

@property (readonly) uint32_t size;


+(id) initWithData:(const char*)data length:(uint32_t)length;

-(const char*) data;
-(void) reset;
-(uint32_t) remain;

-(void) writeChar:(int8_t)val;
-(void) writeByte:(uint8_t)val;
-(void) writeInt16:(int16_t)val;
-(void) writeUInt16:(uint16_t)val;
-(void) writeInt32:(int32_t)val;
-(void) writeUInt32:(uint32_t)val;
-(void) writeInt64: (int64_t) val;
-(void) writeUInt64:(uint64_t) val;
-(void) writeFloat:(float)val;
-(void) writeDouble:(double)val;
-(void) writeString:(NSString*)val;
-(void) writeBytes:(const char*) bytes length:(uint32_t)length;
-(void) writeByteArray:(RpcByteArray*) array;
-(void) writeData:(NSData*) data;

-(int8_t)   readChar ;
-(uint8_t)  readByte;
-(int16_t)  readInt16;
-(uint16_t) readUInt16;
-(int32_t)  readInt32;
-(uint32_t) readUInt32;
-(int64_t)  readInt64;
-(uint64_t) readUInt64;
-(float)    readFloat;
-(double)   readDouble;
-(NSString*)    readString;

-(NSData*) readDataWithSize:(uint32_t)size;
-(NSData*) readData;




@end
