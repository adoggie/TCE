
###file: if-index-list.txt
    
    内容: 
    sns.IBaseServer=100
    sns.ITerminal= 201
    sns.ICtrlServer = 301
    sns.IGateway = 401,false

此文件内容规定了IDL文件内定义的接口服务的序列化编号定义和是否编译生成框架代码。 

###1. 接口interface序列化编号自定义


tce默认的处理方式是将module内的interface从0开始编号

    module{
        interface Animal{
            void run();      
        }
        interface Zoo{
            
        }
    }


以上IDL定义的接口Animal,Zoo 默认的生成接口序号分别是 0,1 
但有时编写IDL是项复杂和繁琐的事情，不同的人员定义的不同interface被集成在一起生成实现代码，这会产生interface序列化编号重复。
为解决interfac编号重复的问题，tce允许人工定义interface的序列化编号 ； 

###2. 框架代码生成控制
程序开发过程中，tce在生成各种语言对应的IDL功能实现代码时，将IDL中的各种数据类型、功能接口统一输出到代码文件，这些文件中包含 客户端使用和服务器侧使用的框架代码。 
当开发的软件工程中不涉及相关interface的调用或实现，则不应该加入到开发工程中。 
if-index-list.txt 可以控制哪个interface是否被输出代码框架. 

    sns.IGateway = 401,false  定义了sns模块的IGateway接口的序列化编号401,当前编译不输出IGateway相关服务器侧实现的相关代码