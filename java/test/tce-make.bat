
del /S /F ..\sns_mobile\*.java
rem python tce2java_xml.py -i sns_mobile.idl -o ../ -p sns_mobile
python tce2java_xml_android.py -i sns_mobile.idl -o ../ -p sns_mobile
pause


