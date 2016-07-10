###Builtin类型映射
tce -> java

    byte => Byte 
    bool => Boolean
    short => Short 
    int   => Integer
    float => Float 
    long  => Long 
    double => Double 
    string => String 
    void   => void 
    

###Sequence

java的Vector<>实现 sequence<>,但并不为sequence<>单独生成类型程序文件

tce:

    sequence<string> namelist_t;
    void collect_names( namelist_t names); 

java:

    void collect_name( Vector<String> names);
        
####byte例外

对于字节数组类型,直接采用java的primitive byte[], 应用于二进制流读写处理
tce:

    sequence<byte> StreamBytes_t;
    StreamBytes_t  bytes;
    void writeBytes( StreamBytes_t content);
java:

    byte [] bytes;
    void writeBytes( byte[] content);
    

###Dictionary 
java 的 HashMap<k,k> 实现 dictionary<k,v>.

< k >必须是tce的primitive类型(byte,bool,short,int,float,long,double,string)

tce :

    dictionay<string,string> Properties_t;
    void setProps(Properties_t props);
    
java: 
    
    void setProps( HashMap< String, String > props)

###Struct
struct被映射为java的class对象 

tce:

    sequence<int> intlist_t ;
    struct Student{
        int  id;
        intlist_t attrs;
        string  name;
    }
    
    dictionary< int , Student> StudentList_t;
    
    StudentList_t getStudents(int max);

java: 
    
    class Student{
        Integer id;
        Vector<Integer> attrs;
        String name;
    }
    
    HashMap<Integer,Student> getStudents(Integer max);
    
###Interface
定义服务接口  
tce
    
    struct time_t{
        int year;
        int month;
        int day;
    }
    
    interface NtpServer{
        time_t syncDateTime();
    }

java

    class time_t{
        Integer year;
        Integer month;
        Integer day;
    }
    
    class NtpServer{
        time_t syncDateTime();
    }
    
####extends 
接口支持继承

tce
    
    interface MyServer extends NtpServer{
        ... 
    }

java

    class MyServer extends NtpServer{
    }
    
    
###Module
module is package 


    
    