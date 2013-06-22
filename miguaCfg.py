#! /usr/bin/env python
#coding=utf-8
"""
本程序通用的一些常量,类似配置文件
"""
from twisted.python import log
from twisted.python.logfile import DailyLogFile
import sys

def setLog(logOn):
    if logOn:
        log.startLogging(DailyLogFile.fromFullPath(LOGFILE))
    else:
        log.startLogging(sys.stdout)

#DB parameter
strHost = '127.0.0.1'
strDB = '5kw_weixin_bird'
strUser = 'kunp'
strPasswd = 'kunx1111'
iPort = 3306

#Log file
LOGFILE = "./miguaWX.log"

#Error code
ErrorCode = "HTTP/1.1 404 Not Found\r\n" + "Connection: close\r\n\r\n"





