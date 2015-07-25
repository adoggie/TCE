tce for java 
===============

tce2java_xml.py  -- 废弃 
tce2java_xml_android.py -- 协议采用xml格式化，底部采用socket通信； 同时支持http的GET/POST请求web服务
tce2java.py -- 底部socket通信，消息采用二进制编码

如果应用采用二进制通信协议，同时又要请求http，那将请求的接口分离开，单独用tce2java.py ,tce2java_xml_android.py进行idl mapping


TCE2
=======
基于之前TCE版本扩展诸多功能特性：
1.支持ios objc语言
2.idl支持module关键字，提供命名空间机制
3.支持多idl文件包含，import 关键字，允许将idl分割为多个idl文件，导入其他接口文件
4.优化mapping生成代码
5.支持module关键字， M::People{}
6.extends支持interface继承,但只能从一个父接口继承
7.同module可以写在不同的idl文件
8.idl文件定义多module
9.void类型函数可以是oneway也可以是twoway
10. void类型函数支持异步调用返回,设置的回调函数被执行，但不携带回调参数

允许空module定义
struct,interface不允许空
接口函数在继承时不能重复