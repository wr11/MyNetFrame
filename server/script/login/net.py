# -*- coding: utf-8 -*-
from protocol import S2C_CONNECT
from myutil.mycorotine import coroutine

import net.netpackage as np

def NetCommand(who, oNetPackage):
	sSub = np.UnpackS(oNetPackage)
	print("【服务端】数据接收完毕 %s" % sSub)
	Handle(who, sSub)

def Handle(who, sSub):
	GetDataFromDs2(sSub)

def GetDataFromDs(sSub):
	import rpc
	oCB = rpc.RpcOnlyCBFunctor(CB_GetDataFromDs, sSub)
	rpc.RemoteCallFunc(2001, oCB, "rpcclient.Test", 1, a=2)
 
def CB_GetDataFromDs(sSub, i, d):
	print("接收到rpc处理结果 %s:%s %s"%(sSub, i, d))

@coroutine
def GetDataFromDs2(sSub):
	from rpc import AsyncCallFunc
	ret = yield AsyncCallFunc(2001, "rpcclient.Test", 1, a=2)
	print("接收到协程rpc处理结果 %s"%(ret))