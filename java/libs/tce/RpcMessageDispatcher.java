package tce;

import java.util.Vector;

/**
 * Created by zhangbin on 16/9/5.
 */
public class RpcMessageDispatcher implements Runnable{

    public interface Client{

        public String getName();
    }

    int _threadNum = 1;
    Vector<RpcMessage> _messages = new Vector<RpcMessage>();
    Vector<Thread>  _threads = new Vector<Thread>();
    boolean _running = false;
    Client _client = null;

    public RpcMessageDispatcher(Client client,int thread_num){
        _client = client;
        _threadNum = thread_num;
    }


    public boolean open(){
        _running = true;

        for(int n=0;n<_threadNum; n++){
            Thread thread = new Thread(this);
            _threads.add(thread);
            thread.start();
        }
        return true;
    }

    public void close(){
        _running = false;
        _messages.notifyAll();
    }


    public void join(){
        try {
            for (Thread thread : _threads) {
                thread.join();
            }
        }catch (Exception e){
            RpcCommunicator.instance().getLogger().error( e.getMessage());
        }
    }

    @Override
    public void run(){
        RpcCommunicator.instance().getLogger().debug("MessageDispatcher Thread enterring..");
        while (_running){

            Vector<RpcMessage> msglist;
            try{
                synchronized (_messages){
	                _messages.wait();
                    msglist = _messages;
                    _messages = new Vector<RpcMessage>();
                }
                for(RpcMessage m:msglist){
                    m.conn.dispatchMsg(m);
                }
            }catch (Exception e){
                RpcCommunicator.instance().getLogger().error(e.getMessage());
            }
        }
        RpcCommunicator.instance().getLogger().debug("MessageDispatcher Thread exiting..");
    }

    public void dispatchMsg(RpcMessage m){
        synchronized (_messages){
            _messages.add(m);
            _messages.notify();
        }
    }

}

