
using System;
using System.IO;
using System.Net;
using System.Text;

namespace Tce {

    public class BinarySerializer {

        
        //读取4字节长度字符串
        public static string readString(BinaryReader reader) {
            int len = 0;
            byte[] bytes;
            string value;
            UTF8Encoding utf8 = new UTF8Encoding();
            len = IPAddress.NetworkToHostOrder(reader.ReadInt32());
            bytes = reader.ReadBytes(len);
            value = utf8.GetString(bytes);
            return value;
        }

        public static short readShort(BinaryReader reader) {
            short value = 0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt16());
            return value;
        }

        public static int readInt(BinaryReader reader) {
            int value = 0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt32());
            return value;
        }

        public static long readInt64(BinaryReader reader) {
            long value =0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt64());
            return value;
        }

        

    }
   

}