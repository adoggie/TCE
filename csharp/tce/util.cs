

using System;

namespace Tce {

    class Utility {
        
        public static int unixTimestamp(System.DateTime time){
            System.DateTime startTime = TimeZone.CurrentTimeZone.ToLocalTime(new System.DateTime(1970, 1, 1));
            return (int)(time - startTime).TotalSeconds;
        }
    }

}