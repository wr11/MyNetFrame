# -*- coding: utf-8 -*-

from operator import index
from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV, CLIENT, SERVER
from protocol import *
from netpackage import *

import twisted
import twisted.internet.protocol
import twisted.internet.reactor
import timer
import mq
import conf

if "g_Connect" not in globals():
	g_Connect = {}

if "g_ClientConnect" not in globals():
	g_ClientConnect = {}

if "g_ClientConnectID" not in globals():
	g_ClientConnectID = 0

#-------------主动连接(作为客户端连接其他服务器)实例---------------
class DeferClient(twisted.internet.protocol.Protocol):

	def SetArgs(self, args):
		self.m_ServerID = args[0]
		self.m_Index = args[1]

	def connectionMade(self):
		global g_Connect
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if (tFlag not in g_Connect.keys()) or (tFlag in g_Connect.keys() and not g_Connect[tFlag].connected):
			g_Connect[tFlag] = self
			print("主动连接%s %s 已建立网络层连接"%tFlag)
			if not timer.GetTimer("SendMq_Handler"):
				timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

			PutData((MQ_LOCALMAKEROUTE, (sHost, iPort, self.m_ServerID, self.m_Index)))
		else:
			self.transport.loseConnection()

	def dataReceived(self, data):
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# PutData((C2S, tFlag, data))
		# print("网络层接收到数据，并已加入消息队列")
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		print("数据来源错误%s %s"%tFlag)

	def connectionLost(self, reason):
		global g_Connect
		print("网络层与服务器断开连接")
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if tFlag in g_Connect:
			del g_Connect[tFlag]

		iServer = self.m_ServerID
		iIndex = self.m_Index
		tFlag1 = (iServer, iIndex)
		PutData((MQ_DISCONNECT, tFlag1))

class DefaultClientFactory(twisted.internet.protocol.ReconnectingClientFactory):
	protocol = DeferClient

	def __init__(self, *args):
		super().__init__()
		self.m_Args = args

	def buildProtocol(self, addr):
		assert self.protocol is not None
		p = self.protocol()
		p.factory = self
		p.SetArgs(self.m_Args)
		return p

#--------------接受连接(作为服务器接受其他客户端的连接)实例---------------
class CServer(twisted.internet.protocol.Protocol):
	def connectionMade(self):
		# global g_Connect
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# if tFlag not in g_Connect.keys():
		# 	g_Connect[tFlag] = self
		# 	print("接收连接%s %s 已建立网络层连接"%tFlag)
		# 	if not timer.GetTimer("SendMq_Handler"):
		# 		timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)
		# else:
		# 	self.transport.loseConnection()
		pass

	def connectionLost(self, reason):
		# global g_Connect
		# print("与服务器断开连接")
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# if tFlag in g_Connect:
		# 	del g_Connect[tFlag]

		# PutData((SELF, MQ_DISCONNECT, tFlag))
		pass


	def dataReceived(self, data):
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		PutData(MQ_DATARECEIVED, data)

class CBaseServerFactory(twisted.internet.protocol.Factory):
	protocol = CServer

#--------------接受连接(作为服务器接受其他客户端的连接)实例---------------
class CClientServer(twisted.internet.protocol.Protocol):
	def connectionMade(self):
		global g_ClientConnect, g_ClientConnectID
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if (tFlag not in g_ClientConnect.keys()) or (tFlag in g_ClientConnect.keys() and not g_ClientConnect[tFlag].connected):
			g_ClientConnect[tFlag] = self
			print("客户端%s %s 已建立网络层连接"%tFlag)
			if not timer.GetTimer("SendMq_Handler"):
				timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

			self.m_ClientConnectID = g_ClientConnectID
			PutData((MQ_CLIENTCONNECT, (sHost, iPort, g_ClientConnectID)))
			g_ClientConnectID += 1
		else:
			self.transport.loseConnection()

	def connectionLost(self, reason):
		iConnectID = self.m_ClientConnectID
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if tFlag in g_ClientConnect:
			del g_ClientConnect[tFlag]
		
		PutData((MQ_CLIENTDISCONNECT, (iConnectID,)))


	def dataReceived(self, data):
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		PutData((MQ_DATARECEIVED, data))

class CClientServerFactory(twisted.internet.protocol.Factory):
	protocol = CClientServer


def run(oSendMq, oRecvMq, oConfInitFunc):
	global g_Connect
	oConfInitFunc()

	mq.SetMq(oSendMq, MSGQUEUE_SEND)
	mq.SetMq(oRecvMq, MSGQUEUE_RECV)

	lstConfigs = conf.GetConnects()
	for tConfig in lstConfigs:
		iServerID, dConfig = tConfig
		sIP = dConfig["sIP"]
		iPort = dConfig["iPort"]
		index = dConfig["iIndex"]
		tFlag = (sIP, iPort)
		if tFlag in g_Connect:
			continue
		twisted.internet.reactor.connectTCP(sIP, iPort, DefaultClientFactory(iServerID, index))
	# twisted.internet.reactor.listenTCP(CSERVER_PORT, CBaseServerFactory())
	sMyIP, iMyPort = conf.GetCurProcessIPAndPort()
	twisted.internet.reactor.listenTCP(iMyPort, CBaseServerFactory())
	if conf.IsGate():
		iClientPort = conf.GetClientPort()
		twisted.internet.reactor.listenTCP(iClientPort, CClientServerFactory())
	print("服务端启动完毕，等待客户端连接")
	twisted.internet.reactor.run()

def SendMq_Handler():
	global g_Connect, g_ClientConnect
	iMax = conf.GetMaxSendNum()
	oMq = mq.GetMq(MSGQUEUE_SEND)
	if oMq.empty():
		timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)
		return
	iHandled = 0
	while not oMq.empty() and iHandled <= iMax:
		iHandled += 1
		tData = oMq.get()
		iTargetType, tFlag, bData = tData
		sIP, iPort = tFlag
		print("消息队列数据准备发送至%s %s %s" % (sIP, iPort))
		if iTargetType == SERVER:
			oProto = g_Connect.get(tFlag, None)
		elif iTargetType == CLIENT:
			oProto = g_ClientConnect.get(tFlag, None)
		else:
			oProto = None
		if oProto:
			oProto.m_Socket.transport.getHandle().sendall(bData)
		else:
			print("WARNING: No connect %s %s"%tFlag)
	timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

def PutData(data):
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	if oRecvMq:
		if oRecvMq.full():
			print("数据在加载")
			return
		oRecvMq.put(data)