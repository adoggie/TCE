# -- coding:utf-8 --

#scott  shanghai china
#86-13916624477 qq:24509826 msn: socketref@hotmail.com
#
Error_FileServer_Base = 2000
EFSB = Error_FileServer_Base
Error_FileWrite_Exception = EFSB+1
Error_FileCreate_Failed = EFSB+2
Error_FileOpen_Failed = EFSB+3 
Error_FilePut_Timeout = EFSB+4
Error_FilePut_Reject = EFSB+5
Error_FileRead_Failed = EFSB+6



Error_FileMedia_Base = 3000
EFMB = Error_FileMedia_Base+1
Error_AllocCodec_Failed = EFMB +1


ERROR_SUCC = 0
	
NETMSG_ERROR_MAGIC = 1
NETMSG_ERROR_SIZE = 2
NETMSG_ERROR_DECOMPRESS =3
NETMSG_ERROR_NOTSUPPORTCOMPRESS = 4
NETMSG_ERROR_MESSAGEUNMARSHALL = 5
NETMSG_ERROR_DESTHOST_UNREACHABLE = 6
NETMSG_ERROR_CONNECTION_LOST =7
NETMSG_ERROR_SENDDATA_FAILED = 8
NETMSG_ERROR_RESPONSE_TIMEOUT = 9
NETMSG_ERROR_INVALID_MSG = 10
