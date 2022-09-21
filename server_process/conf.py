# -*- coding: utf-8 -*-
'''
服务器配置文件
'''

from tkinter.font import NORMAL
from myutil.cachelib.cachefunc import CacheResult

VERSION = 1

GATE = 10	#网关
GPS = 11	#玩法
DBS = 12	#数据落地(redis+mysql)
MCM = 98	#全局集群管理(Master Cluster Manager)
LCM = 99	#本地集群管理(Local Cluster Manager)

LEAD = 1
FOLLOWER = 2
NORMAL = 3

#-----------------server conf----------------
SERVER_CONF = {
	"run_attr":{
		"bDebug" : True,
	},
	"mysql" : {
		"bIsOn":True,
		"host":'localhost',
		"user":'root',
		"password":'mytool2021',
		"db":'mytool_db',
		"charset":'utf8',
	},
	"redis" : {
		"bIsOn":False,
	},
}


#-----------------server allocate----------------
SERVER_ALLOCATE = [
	#Master Cluster Manager Server
	{
		"iServerID" 		:	0,
		"sServerName"		:	"Master Cluster Manager",
		"lstProcessConfig"	:	[
			{
				"iIndex"		:	1,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	10001,
				"iType"			:	MCM,
				"iRole"			:	LEAD,
				"iConcern"		:	2,
			},
			{
				"iIndex"		:	2,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	10002,
				"iType"			:	MCM,
				"iRole"			:	FOLLOWER,
				"iConcern"		:	1,
			},
		],
	},

	#Logic Server1(index 为数组下标加1, iServerID为999加数组下标)
	{
		"iServerID" 		:	1000,
		"sServerName"		:	"ServerTest",
		"lstProcessConfig"	:	[
			{
				"iIndex"		:	1,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	20001,
				"iType"			:	LCM,
			},
			{
				"iIndex"		:	2,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	20002,
				"iType"			:	GATE,
			},
			{
				"iIndex"		:	3,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	20003,
				"iType"			:	GPS,
			},
			{
				"iIndex"		:	4,
				"sIP"			:	"127.0.0.1",
				"iPort"			:	20004,
				"iType"			:	DBS,
			},
		],
	},
]

#-----------------api----------------

if "LOCAL_SERVERNUM" not in globals():
	LOCAL_SERVERNUM = 0
if "LOCAL_SERVERNAME" not in globals():
	LOCAL_SERVERNAME = ""
if "LOCAL_SERVERCONFIG" not in globals():
	LOCAL_SERVERCONFIG = {}

#@CacheResult()
def GetServerConfig(iServerID, iIndex):
	global SERVER_ALLOCATE
	if not(iServerID == 0 or iServerID >= 1000):
		raise Exception("config error: the value of server id must be 0 or bigger than 1000")
	iFlag = 0
	if iServerID > 0:
		iFlag = iServerID - 1000 + 1
	if iFlag < 0 or iFlag > len(SERVER_ALLOCATE) - 1:
		raise Exception("config error: server id %s does not exist" % (iServerID))
	dServerConfig = SERVER_ALLOCATE[iFlag]
	iID = dServerConfig["iServerID"]
	if iID != iServerID:
		raise Exception("config error: server id %s does not match" % (iServerID))
	sName = dServerConfig["sServerName"]
	lstConfig = dServerConfig["lstProcessConfig"]
	if iIndex < 1 or iIndex > len(lstConfig):
		raise Exception("config error: iIndex %s does not exist in server id %s" % (iIndex, iServerID))
	dConfig = lstConfig[iIndex]
	return (sName, dConfig)

def Init(iServerID, iIndex):
	global LOCAL_SERVERNUM, LOCAL_SERVERNAME, LOCAL_SERVERCONFIG
	sName, dConfig = GetServerConfig(iServerID, iIndex)
	LOCAL_SERVERNUM = iServerID
	LOCAL_SERVERNAME = sName
	LOCAL_SERVERCONFIG = dConfig