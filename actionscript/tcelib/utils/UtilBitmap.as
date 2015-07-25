/**
 * utilbitmap.as
 * 位图辅助功能函数
 **/

package tcelib.utils
{
	import flash.display.BitmapData;
	import flash.geom.Matrix;
	import flash.geom.Point;
	
	import flashx.textLayout.formats.Float;

	public class UtilBitmap
	{
		public function UtilBitmap()
		{
		}

		/**
		 * angle - 旋转角度  正值向右，负值向左 
		 * rpoint - 旋转点 默认安 图像左上角旋转
		 */ 
		public static function rotate(bmp:BitmapData,angle:Float,rpoint:Point = Point(0,0) ):BitmapData{  
			var m:Matrix = new Matrix();  
			m.rotate( Math.PI/180.0*angle);  
			//m.translate(bmp.height,0);
			m.translate(rpoint.x,rpoint.y);
			var bd:BitmapData = new BitmapData(bmp.height, bmp.width);  
			bd.draw(bmp,m);  
			return bd;  
		}  
	 	
		/*
		public static function scaleTo(bmp:BitmapData, width:Number,height:Number):BitmapData{
			var m:Matrix = new Matrix();  
			m.scale(width/  
			m.translate(bmp.width/2,height/2);
			var bd:BitmapData = new BitmapData(bmp.height, bmp.width);  
			bd.draw(bmp,m);
			
		}
		*/
			
		
	}
}