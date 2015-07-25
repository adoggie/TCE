# -- coding: utf-8 --


__author__ = 'scott'

import sys,os,traceback,struct


def serial_byte(val,stream):
	return stream + struct.pack('B',val)

def unserial_byte(stream,idx):
	val, = struct.unpack('B',stream[idx:idx+1])
	idx +=1
	return val,idx

def serial_bool(val,stream):
	if val:
		stream += struct.pack('B',1)
	else:
		stream += struct.pack('B',0)
	return stream

def unserial_bool(stream,idx):
	val, = struct.unpack('B',stream[idx:idx+1])
	idx +=1
	if not val:
		val = False
	else:
		val = True
	return val,idx

def serial_short(val,stream):
	return stream + struct.pack('!h',val)

def unserial_short(stream,idx):
	val, = struct.unpack('!h',stream[idx:idx+2])
	idx +=2
	return val,idx

def serial_int(val,stream):
	return stream + struct.pack('!i',val)

def unserial_int(stream,idx):
	val, = struct.unpack('!i',stream[idx:idx+4])
	idx +=4
	return val,idx

def serial_long(val,stream):
	return stream + struct.pack('!q',val)

def unserial_long(stream,idx):
	val, = struct.unpack('!i',stream[idx:idx+8])
	idx +=8
	return val,idx

def serial_float(val,stream):
	return stream + struct.pack('!f',val)

def unserial_float(stream,idx):
	val, = struct.unpack('!f',stream[idx:idx+4])
	idx +=4
	return val,idx

def serial_double(val,stream):
	return stream + struct.pack('!d',val)

def unserial_double(stream,idx):
	val, = struct.unpack('!d',stream[idx:idx+8])
	idx +=8
	return val,idx

def serial_string(val,stream):
	if type(val) != str:
		val = str( val )
	try:
		val = val.encode('utf-8')
	except:
		print 'tce.serial_string() encode utf-8 failed!'
		# traceback.print_exc()
	stream += struct.pack('!I',len(val)) + val
	return stream

def serial_string_8(val,stream):
	if type(val) != str:
		val = str( val )
	try:
		val = val.encode('utf-8')
	except:
		traceback.print_exc()
	size = len(val)
	if size > 256:
		size = 256
		val = val[:size]
	stream += struct.pack('B',size) + val
	return stream

def unserial_string(stream,idx):
	size, = struct.unpack('!I',stream[idx:idx+4])
	idx += 4
	val = stream[idx:idx+size]
	idx += size
	return val,idx

def unserial_string_8(stream,idx):
	size, = struct.unpack('B',stream[idx:idx+1])
	idx += 1
	val = stream[idx:idx+size]
	idx += size
	return val,idx