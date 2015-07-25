 

package tcelib.utils
{
	import flash.utils.Dictionary;

	/**
	 *
	 * Defines the contract for lightweight HashMap implementations
	 * which are to expose an API into a managed collection of key
	 * value pairs
	 *
	 */
	public interface IMap
	{
		/**
		 *
		 * Adds a key / value pair to the current Map
		 *
		 * @param the key to add to the map
		 * @param the value of the specified key
		 *
		 */
		function put(key:*, value:*) : void;

		/**
		 *
		 * Places all name / value pairs into the current
		 * <code>IMap</code> instance.
		 *
		 * @param an <code>Object</code> of name / value pairs
		 *
		 */        
		function putAll(table:Dictionary) : void;

		/**
		 *
		 * <code>putEntry</code> is intended as a pseudo-overloaded
		 * <code>put</code> implementation whereby clients may call
		 * <code>putEntry</code> to pass an <code>IHashMapEntry</code>
		 * implementation.
		 *
		 * @param concrete <code>IHashMapEntry</code> implementation
		 *
		 */        
		function putEntry(entry:IHashMapEntry) : void;

		/**
		 *
		 * Removes a key / value from the HashMap instance
		 *
		 * @param  key to remove from the map
		 *
		 */
		function remove(key:*) : void;

		/**
		 *
		 * Determines if a key exists in the HashMap instance
		 *
		 * @param  the key in which to determine existance in the map
		 * @return true if the key exisits, false if not
		 *
		 */
		function containsKey(key:*) : Boolean;

		/**
		 *
		 * Determines if a value exists in the HashMap instance
		 *
		 * @param  the value in which to determine existance in the map
		 * @return true if the value exisits, false if not
		 *
		 */
		function containsValue(value:*) : Boolean;

		/**
		 *
		 * Returns a key value from the HashMap instance
		 *
		 * @param  the key in which to retrieve the value of
		 * @return the value of the specified key
		 *
		 */
		function getKey(value:*) : *;

		/**
		 *
		 * Returns a key value from the HashMap instance
		 *
		 * @param  the key in which to retrieve the value of
		 * @return the value of the specified key
		 *
		 */
		function getValue(key:*) : *;

		/**
		 *
		 * Returns each key added to the HashMap instance
		 *
		 * @return String Array of key identifiers
		 *
		 */
		function getKeys() : Array;

		/**
		 *
		 * Returns each value assigned to each key in the HashMap instance
		 *
		 * @return Array of values assigned for all keys in the map
		 *
		 */
		function getValues() : Array;

		/**
		 *
		 * Retrieves the size of the HashMap instance
		 *
		 * @return the current size of the map instance
		 *
		 */
		function size() : int;

		/**
		 *
		 * Determines if the HashMap instance is empty
		 *
		 * @return true if the current map is empty, false if not
		 *
		 */
		function isEmpty() : Boolean;

		/**
		 *
		 * Resets all key value assignments in the HashMap instance to null
		 *
		 */
		function reset() : void;    

		/**
		 *
		 * Resets all key / values defined in the HashMap instance to null
		 *
		 */
		function resetAllExcept(key:*) : void;    

		/**
		 *
		 * Clears all key / values defined in the HashMap instance
		 *
		 */
		function clear() : void;

		/**
		 *
		 * Clears all key / values defined in the HashMap instance
		 * with the exception of the specified key
		 *
		 */
		function clearAllExcept(key:*) : void;

		/**
		 *
		 * Returns an <code>Array</code> of <code>IHashMapEntry</code>
		 * objects based on the underlying internal map.
		 *
		 * @param <code>Array</code> of <code>IHashMapEntry</code> objects
		 *
		 */        
		function getEntries() : Array;
	}
}


