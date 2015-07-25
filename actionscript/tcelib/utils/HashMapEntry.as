 

package tcelib.utils
{
	/**
	 *
	 * Provides a strongly typed implementation of a key/value pairs
	 *
	 * @see IHashMapEntry
	 * @see IMap
	 *
	 */    
	public class HashMapEntry implements IHashMapEntry
	{
		/**
		 *
		 * Defines the <code>key</code> property of the key / value
		 * pair.
		 *
		 */
		protected var _key: * ;

		/**
		 *
		 * Defines the <code>value</code> property of the key / value
		 * pair.
		 *
		 */
		protected var _value: * ;

		/**
		 *
		 * <code>HashMapEntry</code> constructor accepts values for
		 * the <code>key</code> and <code>value</code> properties of
		 * an <code>IHashMapEntry</code>
		 *
		 * @param value to assign to the <code>key</code> property
		 * @param value to assign to the <code>value</code> property
		 *
		 */        
		public function HashMapEntry(key:*, value:*)
		{
			this._key   = key;
			this._value = value;
		}

		/**
		 *
		 * Assigns a value to the <code>key</code> property of the
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @param value to assign to the <code>key</code> property
		 *
		 */    
		public function set key(key:*) : void
		{
			_key = key;
		}

		/**
		 *
		 * Retrieves the value of the <code>key</code> property of the
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @return value of the <code>key</code> property
		 *
		 */    
		public function get key() : *
		{
			return _key;
		}

		/**
		 *
		 * Assignes a value to the <code>value</code> property of an
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @param value to assign to the <code>value</code> property
		 *
		 */    
		public function set value(value:*) : void
		{
			_value = value;
		}

		/**
		 *
		 * Retrieves the value of the <code>value</code> property of an
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @return value of the <code>value</code> property
		 *
		 */
		public function get value() : *
		{
			return _value;
		}
	}
}


