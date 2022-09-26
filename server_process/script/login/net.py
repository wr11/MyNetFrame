# -*- coding: utf-8 -*-
from myutil.mycorotine import coroutine

import netpackage as np

def NetCommand(who, oNetPackage):
	sSub = np.UnpackS(oNetPackage)
	PrintDebug("the received data is %s" % sSub)
	# Handle(who, sSub)

def Handle(who, sSub):
	GetDataFromDs(sSub)

def GetDataFromDs(sSub):
	import rpc
	oCB = rpc.RpcOnlyCBFunctor(CB_GetDataFromDs, sSub)
	rpc.RemoteCallFunc(2001, oCB, "rpcclient.Test", 1, a=2)
 
def CB_GetDataFromDs(sSub, i, d):
	PrintDebug("接收到rpc处理结果 %s:%s %s"%(sSub, i, d))

@coroutine
def GetDataFromDs2(sSub):
	from rpc import AsyncRemoteCallFunc
	ret = yield AsyncRemoteCallFunc(2001, "rpcclient.Test", 1, a=2)
	PrintDebug("接收到协程rpc处理结果 %s"%(ret))