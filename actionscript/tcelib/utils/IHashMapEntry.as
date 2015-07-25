 
package tcelib.utils
{
	/**
	 *
	 * Defines the contract for classes which are to provide a specific
	 * implementation of an <code>IMap</code> entry.
	 *
	 * <p>
	 * An <code>Entry</code> object is essentially a sealed type which
	 * defines two properties: <code>key</code> and <code>value</code>
	 * <code>IHashMapEntry</code> provides an interface into an Entry
	 * object. <code>IHashMapEntry</code> implementations are intended
	 * to provide a Strongly typed implementation of a key / values
	 * pair.
	 * </p>
	 *
	 * @see IMap
	 *
	 */    
	public interface IHashMapEntry
	{
		/**
		 *
		 * Assigns a value to the <code>key</code> property of the
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @param value to assign to the <code>key</code> property
		 *
		 */        
		function set key(value:*) : void;

		/**
		 *
		 * Retrieves the value of the <code>key</code> property of the
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @return value of the <code>key</code> property
		 *
		 */            
		function get key() : *;

		/**
		 *
		 * Assignes a value to the <code>value</code> property of an
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @param value to assign to the <code>value</code> property
		 *
		 */        
		function set value(value:*) : void;

		/**
		 *
		 * Retrieves the value of the <code>value</code> property of an
		 * <code>IHashMapEntry</code> implementation.
		 *
		 * @return value of the <code>value</code> property
		 *
		 */        
		function get value() : *;
	}
}


