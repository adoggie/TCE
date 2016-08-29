
using System;
using System.IO;
using System.Net;
using System.Text;

namespace Tce {

    public class RpcBinarySerializer {

        
        //读取4字节长度字符串
        public static string readString(BinaryReader reader) {
            int len = 0;
            byte[] bytes;
            string value;
            UTF8Encoding utf8 = new UTF8Encoding();
            len = readInt(reader);
            bytes = reader.ReadBytes(len);
            value = utf8.GetString(bytes);
            return value;
        }

        public static void writeString(string value, BinaryWriter writer) {
            UTF8Encoding utf8 = new UTF8Encoding();
            int len = utf8.GetByteCount(value);
            len = IPAddress.HostToNetworkOrder(len);
            writeInt(len,writer);
            writer.Write( utf8.GetBytes(value));
        }

        public static int getByteCount(string value) {
            int count = 0;
            UTF8Encoding utf8 = new UTF8Encoding();
            count = utf8.GetByteCount(value);
            return count + 4;
        }

        public static byte readByte(BinaryReader reader) {
            return reader.ReadByte();
        }

        public static void writeByte(byte value, BinaryWriter writer){
            writer.Write(value);
        }

        public static short readShort(BinaryReader reader) {
            short value = 0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt16());
            return value;
        }

        public static void writeShort(short value, BinaryWriter writer) {
            writer.Write( IPAddress.HostToNetworkOrder(value));
        }

        public static int readInt(BinaryReader reader) {
            int value = 0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt32());
            return value;
        }

        public static void writeInt(int value, BinaryWriter writer) {
            writer.Write(IPAddress.HostToNetworkOrder(value));
        }

        public static long readLong(BinaryReader reader) {
            long value =0;
            value = IPAddress.NetworkToHostOrder(reader.ReadInt64());
            return value;
        }

        public static void writeLong(long value, BinaryWriter writer) {
            writer.Write(IPAddress.HostToNetworkOrder(value));
        }

        public static float readFloat(BinaryReader reader) {
            byte[] bytes = reader.ReadBytes(4);
            float value = BitConverter.ToSingle(bytes, 0);
            return value;
        }

        public static void writeFloat(float value,BinaryWriter writer) {
            byte[] bytes = BitConverter.GetBytes(value);
            writer.Write(bytes);
        }

        public static double readDouble(BinaryReader reader)
        {
            byte[] bytes = reader.ReadBytes(8);
            double value = BitConverter.ToDouble(bytes, 0);
            return value;
        }

        public static void writeDouble(double value, BinaryWriter writer)
        {
            byte[] bytes = BitConverter.GetBytes(value);
            writer.Write(bytes);
        }

        public static bool readBool(BinaryReader reader) {
            byte val = readByte(reader);
            return val == 1 ? true : false;
        }

        public static void writeBool(bool value, BinaryWriter writer) {
            byte byteval = value ? (byte)1 : (byte)0;
            writeByte(byteval,writer);
        }

        //readBytes 
        // 1. read 4 bytes header 
        // 2. read rest data 
        public static byte[] readBytes(BinaryReader reader) {
            byte[] value = null;
            int size = reader.ReadInt32();
            value = reader.ReadBytes(size);
            return value;
        }

        public static void writeBytes(byte[] value, BinaryWriter writer) {
            writeInt(value.Length,writer);
            writer.Write(value);
        }
    }
   

}