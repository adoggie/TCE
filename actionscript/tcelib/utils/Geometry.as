package tcelib.utils
{
	public class Geometry
	{
		public function Geometry()
		{
		}
		
		public static function splitRectArray(s:String):Array{
			var wkt:Array;
			wkt = s.split(",")
			var x:Number,y:Number,w:Number,h:Number;
			x = parseFloat(wkt[0]);
			y = parseFloat(wkt[1]);
			w = parseFloat(wkt[2]);
			h = parseFloat(wkt[3]);
			return [x,y,w,h];
		}
	}
}