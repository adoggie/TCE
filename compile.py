import sys,time,os,py_compile
files=['tce2py.py','tce2java.py','tce2js.py','tce_util.py']

for file in files:
	py_compile.compile(file)

