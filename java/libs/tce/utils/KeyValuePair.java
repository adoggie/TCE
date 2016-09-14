package tce.utils;

/**
 * Created by zhangbin on 16/9/13.
 */
public class KeyValuePair<K,V> {
    private  K _key;
    private  V _value;

    public K getKey() {
        return _key;
    }

    public void setKey(K _key) {
        this._key = _key;
    }

    public V getValue() {
        return _value;
    }

    public void setValue(V _value) {
        this._value = _value;
    }

    public KeyValuePair(K key,V value){
        _key = key;
        _value = value;
    }


}
