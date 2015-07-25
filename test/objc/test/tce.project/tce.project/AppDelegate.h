//
//  AppDelegate.h
//  tce.project
//
//  Created by zhang bin on 14-1-16.
//  Copyright (c) 2014 zhang bin. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface AppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;
@property uint32_t age;

-(void)test;
-(void)test2:(int (^)(int * pint,NSString*name)) callback;

@end