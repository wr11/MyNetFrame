# -*- coding: utf-8 -*-

import conf
import time
import traceback

LOG_FUNC = print
LOCAL_THREAD = ""
LOCAL_FLAG = ""

#PrintDebug type
DEBUG = 1
WARNING = 2
ERROR = 3
STACK = 4

TYPE2DESC = {
	DEBUG : "DEBUG",
	WARNING : "WARNING",
	ERROR : "ERROR",
	STACK : "STACK",
}

def Init(sThread):
	global LOCAL_FLAG, LOCAL_THREAD
	sProcessName, iIndex = conf.GetProcessName(), conf.GetProcessIndex()
	LOCAL_FLAG = "%s_%s"%(sProcessName, iIndex)
	LOCAL_THREAD = sThread
	import builtins
	iterGlobalKey = globals().keys()
	for sKey in iterGlobalKey:
		if sKey.startswith("Print"):
			builtins.__dict__[sKey] = globals()[sKey]

	PrintDebug("Logger inited")

def GetCommonLogHeader(iType):
	global LOCAL_FLAG, LOCAL_THREAD
	sTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	lstTraceMsg = traceback.format_stack()[-3].split(",")
	sFile = lstTraceMsg[0].replace("\\", "/").split("/")[-1][:-1]	#[:-1]去掉多余的 "
	sLine = lstTraceMsg[1]
	sFormatTime = "[%s]"%sTime
	sFormatProc = "[%s:%s]"%(LOCAL_FLAG, LOCAL_THREAD)
	sFormatType = "[%s]"%TYPE2DESC[iType]
	sFormatLocate = "[%s:%s]"%(sFile, sLine)
	return "%s%s%s%s"%(sFormatTime, sFormatProc, sFormatLocate, sFormatType)


def PrintDebug(*args):
	if not conf.IsDebug():
		return
	sHeader = GetCommonLogHeader(DEBUG)
	LOG_FUNC(sHeader, *args)

def PrintError(*args):
	sHeader = GetCommonLogHeader(ERROR)
	LOG_FUNC(sHeader, *args)

def PrintWarning(*args):
	sHeader = GetCommonLogHeader(WARNING)
	LOG_FUNC(sHeader, *args)

def PrintStack(*args):
	if not conf.IsDebug():
		return
	sHeader = GetCommonLogHeader(WARNING)
	LOG_FUNC("%s\n"%sHeader)
	traceback.print_stack()