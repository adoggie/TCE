#coding:utf-8
__author__ = 'scott'

import string ,time ,threading,traceback
import tce


LOG_DEBUG = 1
LOG_WARN = 2
LOG_INFO = 3
LOG_ERROR = 4

def log_print(m,what):
	from communicator import RpcCommunicator
	logger= RpcCommunicator.instance().getLogger()
	if not logger:  return
	if what == LOG_DEBUG:
		logger.debug(m)
	elif what == LOG_WARN:
		logger.warning(m)
	elif what == LOG_INFO:
		logger.trace(m)
	elif what == LOG_ERROR:
		logger.error(m)


def log_debug(m):
	log_print(m,LOG_DEBUG)

def log_warn(m):
	log_print(m,LOG_WARN)


def log_info(m):
	log_print(m,LOG_INFO)

def log_error(m):
	log_print(m,LOG_ERROR)

'''
Logger
bin.zhang@autonavi.com 2012.3
'''

class LogHandler:
	def __init__(self,name):
		self.name = name

	def write(self,d):
		return True

	def open(self):
		return True

	def destroy(self):
		return True

'''
FileHandler
默认存储1天的日志数据，文件以追加模式打开
'''
class FileHandler(LogHandler):
	def __init__(self,name,subfix='_%Y%m%d_%H%M%S.txt',cycle= 24*3600,linesep='\n'):
		LogHandler.__init__(self,name)
		self.cycletime = cycle #存储周期
		self.linesep = linesep
		self.filename = name+'.log'
		self.newtime = time.time()
		self.subfix = subfix
		self.fp = None
		self.mtxfile = threading.Lock()

	def open(self):
		try:
			if self.fp: self.fp.close()
			self.newtime = time.time()
			now = time.localtime(time.time())

			timestr = time.strftime(self.subfix,now)
			self.filename = "%s%s"%(self.name,timestr)
			self.fp = open(self.filename,'a')
		except:
			traceback.print_exc()
			return False
		return True


	def destroy(self):
		self.fp.close()

	def write(self,d):
		try:
			if time.time() - self.newtime >= self.cycletime:
				self.open()
			self.fp.write(d+self.linesep)
			self.fp.flush()
		except:
			traceback.print_exc()
			return False
		return True

class stdout(LogHandler):
	def __init__(self,name='stdout'):
		LogHandler.__init__(self,name)

	def write(self,d):
		print d

class Logger:
	def __init__(self,name,func=None):
		self.name = name
		self.func = func
		self.formats = "{time} {level} {detail} "
		self.handlers=[]
		self.mtxlog = threading.Lock()

	def addHandler(self,h):
		self.handlers.append(h)
		h.open()
		return self

	def removeHandler(self,name):
		pass

	def setformat(self,formats):
		self.formats = formats
		return self

	def __write(self,d):

		self.mtxlog.acquire()
		try:
			now = time.localtime(time.time())
			timestr = time.strftime('%Y%m%d %H:%M:%S',now)
			d = d.replace('{time}',timestr)
			for h in self.handlers:
				h.write(d)
			if self.func:
				self.func(d)
		except:
			traceback.print_exc()
		self.mtxlog.release()



	def debug(self,*d):
		d = string.join(map(str,d))
		d = self.formats.replace('{detail}',d)
		d = d.replace('{level}','DEBUG')
		self.__write(d)
		return self

	def warning(self,*d):
		d = string.join(map(str,d))
		d = self.formats.replace('{detail}',d)
		d = d.replace('{level}','WARNING')
		self.__write(d)
		return self

	def critical(self,*d):
		d = string.join(map(str,d))
		d = self.formats.replace('{detail}',d)
		d = d.replace('{level}','CRITICAL')
		self.__write(d)
		return self

	def trace(self,*d):
		d = string.join(map(str,d))
		d = self.formats.replace('{detail}',d)
		d = d.replace('{level}','TRACE')
		self.__write(d)
		return self

	def error(self,*d):
		d = string.join(map(str,d))
		d = self.formats.replace('{detail}',d)
		d = d.replace('{level}','ERROR')
		self.__write(d)
		return self




if __name__=='__main__':
	log = Logger('test').addHandler(stdout()).addHandler(FileHandler('abc'))
	for n in range(100):
		log.debug('test log..')
		log.warning('test warning..')
