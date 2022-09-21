# -*- coding: utf-8 -*-
'''
服务器配置文件
'''

GATE = 1	#网关
GPS = 2		#玩法
LGS = 3		#登录
DBS = 4		#数据落地(redis+mysql)


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
class CServer:
	m_Type = 0
	m_IP = ""
	m_Port = 0
	m_Index = 0