# -*- coding: utf-8 -*-
'''
服务器配置文件
'''

from tkinter.font import NORMAL
from myutil.cachelib.cachefunc import CacheResult

VERSION = 1

GATE	=	1<<0		#网关
GPS 	=	1<<1		#玩法
DBS 	=	1<<2		#数据落地(redis+mysql)
LGS 	=	1<<3		#登录
MCM 	=	1<<4		#全局集群管理(Master Cluster Manager)
LCM 	= 	1<<5		#本地集群管理(Local Cluster Manager)

ALL_PROC = GATE|GPS|DBS|LGS|MCM|LCM

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
		"config":{},
	},
}


#-----------------server allocate----------------
'''
服务器集群配置

SERVER_ALLOCATE为列表

1.
Master Cluster Manager位于该列表0的位置
其他服依次往后排列

2.
Master Cluster Manager由LEAD和FOLLOWERS组成

3.
lstProcessConfig中index从一开始依次增加1
port从10000开始即可
服务器编号为1000+数组下标

4.
MCM仅与每个服的LCM通信(即LCM会上报当前服各进程状态)

5.
GPS和DBS数量应对应
'''
SERVER_ALLOCATE = [
	#Master Cluster Manager Server
	{
		"iServerID" 		:	0,
		"sServerName"		:	"Master Cluster Manager",
		"lstProcessConfig"	:	[
			{
				"iIndex"		:	1,
				"sIP"			:	"localhost",
				"iPort"			:	10001,
				"iType"			:	MCM,
				"iRole"			:	LEAD,
				"iConcern"		:	2,
			},
			{
				"iIndex"		:	2,
				"sIP"			:	"localhost",
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
				"sIP"			:	"localhost",
				"iPort"			:	20001,
				"iType"			:	LCM,
			},
			{
				"iIndex"		:	2,
				"sIP"			:	"localhost",
				"iPort"			:	20002,
				"iType"			:	GATE,
			},
			{
				"iIndex"		:	3,
				"sIP"			:	"localhost",
				"iPort"			:	20003,
				"iType"			:	GPS,
			},
			{
				"iIndex"		:	4,
				"sIP"			:	"localhost",
				"iPort"			:	20004,
				"iType"			:	DBS,
			},
			{
				"iIndex"		:	5,
				"sIP"			:	"localhost",
				"iPort"			:	20005,
				"iType"			:	LGS,
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

def IsDebug():
	return SERVER_CONF["run_attr"]["bDebug"]

def IsRedisOn():
	return SERVER_CONF["redis"]["bIsOn"]

def GetRedisConfig():
	return SERVER_CONF["redis"]["config"]

def GetMysqlConfig():
	return SERVER_CONF["mysql"]

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
	dConfig = lstConfig[iIndex - 1]
	return (sName, dConfig)

def Init(iServerID, iIndex):
	global LOCAL_SERVERNUM, LOCAL_SERVERNAME, LOCAL_SERVERCONFIG
	sName, dConfig = GetServerConfig(iServerID, iIndex)
	LOCAL_SERVERNUM = iServerID
	LOCAL_SERVERNAME = sName
	LOCAL_SERVERCONFIG = dConfig

def GetCurProcessType():
	return LOCAL_SERVERCONFIG["iType"]

def GetConnects():
	global LOCAL_SERVERNUM, LOCAL_SERVERCONFIG
	lstResult = []
	iType = GetCurProcessType()
	iRole = LOCAL_SERVERCONFIG.get("iRole", NORMAL)
	iConcernType = 0
	if iType == MCM and iRole == LEAD:
		iConcernType = LCM
	elif iType == LCM:
		iConcernType = ALL_PROC ^ LCM
	elif iType == GATE:
		iConcernType = LCM | LGS | GPS
	elif iType == LGS:
		iConcernType = GATE | DBS | GPS
	elif iType == GPS:
		iConcernType = GATE | DBS | LGS
	elif iType == DBS:
		iConcernType = GPS | LGS

	for dServer in SERVER_ALLOCATE:
		lstConfigs = dServer["lstProcessConfig"]
		if SERVER_ALLOCATE.index(dServer) == 0:
			continue
		for dConfig in lstConfigs:
			iConfigType = dConfig["iType"]
			if iConfigType & iConcernType:
				lstResult.append((dServer["iServerID"], dConfig))

	lstMCMConfig = SERVER_ALLOCATE[0]["lstProcessConfig"]
	if iType == MCM and iRole == LEAD:
		for dConfig1 in lstMCMConfig:
			if dConfig1["iRole"] == FOLLOWER:
				lstResult.append((0, dConfig1))
	elif (iType == MCM and iRole == FOLLOWER) or iType == LCM:
		for dConfig2 in lstMCMConfig:
			if dConfig2["iRole"] == LEAD:
				lstResult.append((0, dConfig2))
				break

	return lstResult