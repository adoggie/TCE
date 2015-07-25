
examples for demostrating how to use tce for javascript.
====

main files:
    test_simple.html
    test.js
    tce.js

make_idl.sh

if-index-list.txt
    *自定义的接口序号
    sns.IBaseServer=100,false
    100 - 接口序号
    false - 是否生成框架代码（服务端接口不要在前端js输出)

related module:
    $tce/test/python/examples/cluster
        gateway.py
        server.py

test_simple.html 将于 gateway.py , server.py 进行互动，演示如何进行rpc调用和服务器推送调用。



ssl websocket:
=============
启用 SSL的websocket：
 在打开websocket之前，浏览器必须已经通过SSL请求验证 ,
 浏览器中先请求  https://server1:16006,经过用户确认验证之后才可进行之后的wss的连接
 var ws = new WebSocket('wss://server1:16006');
 否则直接建立wss的socket连接将报错
