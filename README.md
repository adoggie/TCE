TCE
--------------
TINY COMMUNICATION ENGINE

开发tce是在学习zeroc代码之后产生的想法，原因在于 zeroc的rpc里面有很多我认为是比较累赘的东西，本想将其瘦身，后来发现代码关联太紧，花时间去改造还不如自己实习一套。
我需要的rpc应该是轻量级的、灵活的、易扩展的，与开发技术、网络、平台、通信协议、应用无关。 rpc应提供简易的编程接口，简化网络编程的工作，避免重复造轮子的过程。

Tce为构建移动互联网提供快速的、低成本、高效的解决方案，提供大规模终端接入、集群分布计算、海量存储、反向消息推送等基础服务功能。


Tce实现RPC的内容：
----------------
 1. 接口定义 
 2. 数据序列化 
 3. 通信传输
 4. 消息分派 
 5. 调用模型 (5种)

1. 多语言支持 
----------------
 1. c++ ( stl/boost/asio) *
 2. actionscript 
 3. java
 4. python (gevent/libev/websocket) *
 5. javascript 
 6. php
 7. object-c
 8. node-js
  
2. 系统平台 
----------------
 1. android
 2. ios
 3. html5 
 4. windows/linux (c++/java supported)
  
3. 网络通信
----------------
 1. socket （tcp）
 2. mq 		(qpid,zeromq,easymq)
 3. websocket  (http)
 

更多.. 
----------------
 $TCE/doc/tce.md
 

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#



