//
//  ViewController.m
//  tce.project
//
//  Created by zhang bin on 14-1-16.
//  Copyright (c) 2014 zhang bin. All rights reserved.
//

#import "ViewController.h"
#import "tce.h"
#import "sns.h"

@interface ViewController (){
    RpcCommAdapter * _adapter;
    RpcConnection * _connServer;
    IMessageServerProxy *_prxServer;
}

@property (weak, nonatomic) IBOutlet UIButton *btn1;
@property (weak, nonatomic) IBOutlet UITextField *edtMyId;
@property (weak, nonatomic) IBOutlet UITextField *edtPeerId;
@property (weak, nonatomic) IBOutlet UITextField *edtContent;
@property (weak, nonatomic) IBOutlet UITextField *edtRecieved;

@end

@interface MyTerminal:ITerminal
@property ViewController * viewController;
@end


@implementation MyTerminal
- (instancetype)init:(ViewController *)vc{
    self = [super init];
    if (self) {
        self.viewController = vc;
    }

    return self;
}


//** import **
// 异步接收，此函数运行在非主线程，所以必须通过主线程提交UI数据更新，这里使用 GCD
- (void)onMessage:(Message_t *)message context:(RpcContext *)ctx {
    NSLog(@"recieved message:%@",message.content);

    dispatch_queue_t mainQueue= dispatch_get_main_queue();
    dispatch_sync(mainQueue, ^{
        [self.viewController.edtRecieved setText:message.content] ;
    });
}

@end


@implementation ViewController
- (IBAction)onButton1:(id)sender {

	
}

-(void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex{
	NSLog(@"you click %@:%d",@"name",(int)buttonIndex);
}

-(void)alertView:(UIAlertView *)alertView willDismissWithButtonIndex:(NSInteger)buttonIndex{

}


-(void)onButtonClick{
	if ( self.edtContent.text.length == 0){
		NSLog(@"content must some words");
        [self.view endEditing:YES];
        [[[UIAlertView alloc] initWithTitle:@"" message:@"必须写点啥呀!" delegate:self cancelButtonTitle:@"Okay" otherButtonTitles:nil] show];

        return ;
    }
    Message_t *msg = [Message_t new];
    msg.content = self.edtContent.text;
    NSString * target = self.edtPeerId.text;
    [self->_prxServer postMessage_oneway:target msg:msg props:nil];

}

NSString* CURRENT_USER_ID = @"A1004";

-(void)initRpc{
	[[RpcCommunicator instance] initialize];
    self->_adapter = [[RpcCommunicator instance] createAdapter:@"adapter"];
    MyTerminal *servant = [[MyTerminal alloc] init:self];
    self->_prxServer = [IMessageServerProxy createWithInetAddressHost:@"192.168.199.176" andPort:12002];
    [self->_adapter addServant:servant];
    [self->_adapter addConnection:[self->_prxServer conn]];
    [[RpcCommunicator instance] addAdapter:self->_adapter];
    [[self->_prxServer conn] setToken:CURRENT_USER_ID];


}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
	[[self edtMyId] setText:CURRENT_USER_ID];
	self.edtPeerId.text = @"A1003";
	
	[self.btn1 addTarget:self action:@selector(onButtonClick) forControlEvents:UIControlEventTouchUpInside];
    [self initRpc];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end