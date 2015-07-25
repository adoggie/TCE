//
//  AppDelegate.m
//  tce.project
//
//  Created by zhang bin on 14-1-16.
//  Copyright (c) 2014 zhang bin. All rights reserved.
//

#import "AppDelegate.h"

#import "RpcMessage.h"
//#import "RpcMessageCall.h"

//#import "tce.h"
//#import "RpcConnectionTcpStream.h"
#import "test3.h"


@implementation AppDelegate


-(void) test{
    Location_t* location = [Location_t new];
    RpcByteArray* bar = [RpcByteArray new];
    location.address.postcode = @"201114";
    location.lon = 121.34;
    location.lat = 31.11;
    
    [location marshall:bar];
    
    location = [Location_t new];
    @try {
         [location unmarshall:bar];
    }
    @catch (NSException *exception) {
        NSLog(@"%@", [exception callStackSymbols]);
    }
    @finally {
        
    }
   
    
    
//    [self test2: ^int(int * pint,NSString*name){
//        return 1;
//    }];
//    
//    int (^func)(int*,NSString*) = ^int(int* pint,NSString* name){ return 0 ;};
//    id funx = func;
//    func = (int (^)(int*,NSString*)) funx;
//    func = funx;
//    func((int*)100,@"abc");
//    funx(100);
}

-(void)test2:(int (^)(int * pint,NSString*name)) callback{
    id  cb = callback;
    
}

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
	RpcMessage *msg1 = [[RpcMessage alloc] init];
    RpcMessage *msg2 = [[RpcMessage alloc] init];

    [self test];
    
    bool check = [msg1 isEqual:msg2];;
    msg2 = nil;
    if( msg2){
        NSLog(@"nil test");
    }
    
//	[msg retainCount ]
//	NSLog(@"retain:%d", [m]);
//    msg->call_id = RpcMsgCallType_CALL ;
//    msg = [[RpcMessageCall alloc] init];
//    NSLog(@"%d",msg.calltype);
//    [RpcMessage unmarshall:nil];
    self.age = 100;
    self.window = nil;
    
    NSMutableDictionary* dict = [NSMutableDictionary new];
    [dict setObject:@"scott" forKey:[NSNumber numberWithInt:100]];
    NSNumber* key = [NSNumber numberWithInt:100];
    BOOL test = [key isEqual:[NSNumber numberWithInt:100]];
    NSLog(@"value:%@", [dict objectForKey: @"fucn"]);
    return YES;
}
							
- (void)applicationWillResignActive:(UIApplication *)application
{
    // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
    // Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.

}

- (void)applicationDidEnterBackground:(UIApplication *)application
{
    // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
    // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.

}

- (void)applicationWillEnterForeground:(UIApplication *)application
{
    // Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.

}

- (void)applicationDidBecomeActive:(UIApplication *)application
{
    // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.

}

- (void)applicationWillTerminate:(UIApplication *)application
{
    // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.

}

@end