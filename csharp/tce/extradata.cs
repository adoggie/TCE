
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;

namespace Tce {

   public  class RpcExtraData {

       public RpcExtraData(){

        }

        public bool marshall(MemoryStream d){
            try{
                BinaryWriter writer = new BinaryWriter(d);
                if (_props == null){
                    _props = new Dictionary<string, string>();
                }
                //d.writeInt(_props.size());
                writer.Write((uint)_props.Count);

                UTF8Encoding utf8 = new UTF8Encoding();
                foreach (KeyValuePair<string, string> kv in _props) {
                    writer.Write((uint)kv.Key.Length);
                    writer.Write( utf8.GetBytes(kv.Key));
                    writer.Write((uint)kv.Value.Length);
                    writer.Write(utf8.GetBytes(kv.Value));
                }
            }
            catch (Exception e){
                return false;
            }
            return true;
        }

        //BinaryReader 以 Little-Endian 格式读取此数据类型。
       // Network Order is Big-Endian 
        public bool unmarshall(MemoryStream d){
            try{
                BinaryReader reader = new BinaryReader(d);
                int size = 0;
                size = IPAddress.NetworkToHostOrder( reader.ReadInt32() );

                string key, val;
                byte[] bytes;
                int len = 0;
                UTF8Encoding utf8 = new UTF8Encoding();
                for (int n = 0; n < size; n++) {
                    len = IPAddress.NetworkToHostOrder( reader.ReadInt32() );
                    bytes = reader.ReadBytes(len);
                    key = utf8.GetString(bytes);

                    len = IPAddress.NetworkToHostOrder(reader.ReadInt32());
                    bytes = reader.ReadBytes(len);
                    val = utf8.GetString(bytes);
                    _props.Add(key,val);
                }
            }catch (Exception e){
                RpcCommunicator.instance().getLogger().error(e.ToString());
                return false;
            }
            return true;
        }

        public Dictionary<string, string> getProperties(){
            return _props;
        }

        public string getPropertyValue(string key){
            Dictionary<string, string> props = getProperties();
            if (props.ContainsKey(key)){
                return props[key];
            }
            return null;
        }

        public void setPropertyValue(String key, String value){
            if (_props == null){
                _props = new Dictionary<string, string>();
            }
            _props.Add(key, value);
        }

        public RpcExtraData setProperties(Dictionary<string, string> props){
            if (props != null){
                _props = props;
            }
            return this;
        }

        public int size(){
            return datasize() + 4;
        }


       // cha ,java 里面有个bug啊，计算datasize有问题，回过头去改一下(python,...其他有没有问题啊，查查！）
        public int datasize(){
            int size = 0;
            string key, val;
            UTF8Encoding utf8 = new UTF8Encoding();
            foreach (KeyValuePair<string, string> kv in _props) {
                size += utf8.GetByteCount(kv.Key) + utf8.GetByteCount(kv.Value) + 8;
            }
            return size;
        }

        Dictionary<string, string> _props = new Dictionary<string, string>();


    }

}