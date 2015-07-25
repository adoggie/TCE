# -- coding:utf-8 --

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading
import datetime,string


class _x:
	"""
	从简单数据类型转换成python对象

	p = _x({'name':'boob','body':{'color':'black'},'toys':[1,2,3,],'age':100})
	print p['toys'][1]
	print len(p.toys)
	print p.body.colors
	"""
	def __init__(self,primitive):
		self.data = primitive

	def __getattr__(self, item):
		value = self.data.get(item,None)
		if type(value) == dict:
			value = _x(value)
		return value

	def __len__(self):
		return len(self.data)

	def __str__(self):
		return str(self.data)

	def __getitem__(self, item):
		value = None
		if type(self.data) in (list,tuple):
			value = self.data[item]
			if type(value) in (dict,list,tuple):
				value = _x(value)
		elif type(self.data) == dict:
			value = self.__getattr__(item)
		return value


def getmtime(file):
	try:
		return os.path.getmtime(file)
	except: return 0


def getfiledigest(file,bufsize=1024*5,type='md5'):
	import md5
	m = md5.new()
	try:
		fp = open(file,'rb')
		while True:
			data = fp.read(bufsize)
			if not data:break
			m.update(data)
	except:
		traceback.print_exc()
		return ''
	return m.hexdigest()
	
def setmtime(file,tick): # tick - unix timestamp 1970~
	os.utime(file,(tick,tick) )
	
def getdbsequence_pg(dbconn,seqname):
	seq = 0
	try:
		sql = "select nextval('%s')"%seqname
		cr = dbconn.cursor()
		cr.execute(sql)
		seq = cr.fetchone()[0]
	except:
		traceback.print_exc()
	return seq


def loadjson(file):
	d = None
	try:
		fd = open(file)
		cont = fd.read().strip()
		cont = cont.replace(' ','')
		cont = cont.replace('\'',"\"")
		cont = cont.replace('\t',"")
		cont = cont.replace('(',"[")
		cont = cont.replace(')',"]")
#		print cont
		fd.close()
		d = json.loads(cont)
	except:
		traceback.print_exc()
		pass #traceback.print_exc()
	return d
	
def waitForShutdown():
	time.sleep(1*10000*10)

def genTempFileName():
	return str(time.time())

# unix timestamp to datetime.datetime	
def mk_datetime(timestamp):
	timestamp = int(timestamp)
	return datetime.datetime.fromtimestamp(timestamp)

def formatTimestamp(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d%02d%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		return ''

def formatTimestamp2(secs):
	try:
		dt = datetime.datetime.fromtimestamp(secs)
		return "%04d.%02d.%02d %02d:%02d:%02d"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
	except:
		traceback.print_exc()
		return ''
	
#根据datetime产生timestamp	
def maketimestamp(dt):
	return time.mktime(dt.timetuple())

def touchfile(file):
	try:
		fp = open(file,'w')
		fp.close()
	except:
		return False
	return True

def getToDayStr():
	t = time.localtime()
	return "%04d%02d%02d"%(t.tm_year,t.tm_mon,t.tm_mday)


#这个class用于异步等待获取返回对象之用
class MutexObject:
	def __init__(self):
		self.mtx = threading.Condition()
		self.d = None
		
	def waitObject(self,timeout):
		d = None
		self.mtx.acquire()
		if self.d == None:
			if timeout:
				self.mtx.wait(timeout)
			else:
				self.mtx.wait()
			d = self.d
			self.d = None
		self.mtx.release()
		return d
		
	def notify(self,d):
		self.mtx.acquire()
		self.d = d
		self.mtx.notify()
		self.mtx.release()

def geo_rect2wktpolygon(rc):
	# rc - (x,y,w,h)
	x,y,w,h = rc
	return "POLYGON((%s %s,%s %s,%s %s,%s %s,%s %s))"%\
		(x,y,x+w,y,x+w,y+h,x,y+h,x,y)

def readImageTimes(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	detail = os.popen3('%s -i %s'%(ffmpeg,imagefile) )[2].read()
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return (0,0)
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	lastmodify = os.path.getmtime(imagefile)
	createsecs =  lastmodify - duration_secs
	return (int(createsecs),int(lastmodify))

def statevfs(path):
	import win32api
	import os.path
	path = os.path.normpath(path)
	if path[-1]=='\\':
		path = path[:-1]
	try:
		f,all,user = win32api.GetDiskFreeSpaceEx(path)
		return all,user
	except:return 0,0
	
def hashobject(obj):
	attrs = [s for  s in dir(obj) if not s.startswith('__')]
	kvs={}
	for k in attrs:
		kvs[k] = getattr(obj, k)
	#kvs = {k:getattr(obj, k) for k in attrs}
	return kvs

MB_SIZE = 1024.*1024.
def formatfilesize(size):
	mb = round(size/MB_SIZE,3)
	return mb



def readImageTimes(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	imagefile = os.path.normpath(imagefile)
	detail = os.popen3('c:/dvr_bin/ffmpeg.exe -i %s'%(imagefile) )[2].read()
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return ()
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	lastmodify = os.path.getmtime(imagefile)
	createsecs =  lastmodify - duration_secs
	return (int(createsecs),int(lastmodify))


def parseNetAddr(pdest):
	if type(pdest) == type(''):
		pp = pdest.split(':')
		if len(pp)<2:
			pp = pdest.split(' ')
		pp = filter(lambda x:x!='',pp)
		pdest = (pp[0],int(pp[1]))
	return pdest


class SimpleConfig:
	def __init__(self):
		self.props={}

	def load(self,file):
		try:
			fd = open(file)
			lines = fd.readlines()
			fd.close()
			for line in lines:
				line = line.strip()
				if not line:
					continue
				if line[0]=='#': continue
				idx = line.find('#')
				if idx!=-1:
					line = line[:idx]
				try:
					k,v = map(string.strip,line.split('='))
					if  k:
						self.props[k] = v
				except:
					pass
					#traceback.print_exc()
		except:
			return False
		return True

	def get(self,key,d=None):
		val = self.props.get(key)
		if val == None:
			val = d
		return val


class ReadWriteLock:
	"""A lock object that allows many simultaneous "read-locks", but
only one "write-lock"."""

	def __init__(self):
		self._read_ready = threading.Condition(threading.Lock())
		self._readers = 0

	def acquire_read(self):
		"""Acquire a read-lock. Blocks only if some thread has
acquired write-lock."""
		self._read_ready.acquire()
		try:
			self._readers += 1
		finally:
			self._read_ready.release()

	def release_read(self):
		"""Release a read-lock."""
		self._read_ready.acquire()
		try:
			self._readers -= 1
			if not self._readers:
				self._read_ready.notifyAll()
		finally:
			self._read_ready.release()

	def acquire_write(self):
		"""Acquire a write lock. Blocks until there are no
acquired read- or write-locks."""
		self._read_ready.acquire()
		while self._readers > 0:
			self._read_ready.wait()

	def release_write(self):
		"""Release a write-lock."""
		self._read_ready.release()



def booleanValueOfString(s):
	s = s.strip().lower()
	if s in ('1','true'):
		return True
	return False

def intValueOfString(s,defaultValue=0):
	s = s.strip().lower()
	iv = defaultValue
	try:
		iv = int(s)
	except:
		pass
	return iv



if __name__=='__main__':
	#print loadjson('node.txt')
	#print statevfs('d:/temp4/')
	#print getfiledigest('D:/test_dvr_data/stosync/file0014.trp')
	print readImageTimes(u'P:/20120523/沪EN3870/1-2/DCIM/100MEDIA/FILE0006.MOV'.encode('gbk'))
