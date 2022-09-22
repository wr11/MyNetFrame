# -*- coding: utf-8 -*-

from operator import index
from pubdefines import CSERVER_PORT, MSGQUEUE_SEND, MSGQUEUE_RECV, DELAY_TIME, CallManagerFunc, C2S, S2S, SSERVER_PORT, SELF
from protocol import S2C_CONNECT, SELF_LOCALMAP, SS_IDENTIFY
from net.netpackage import *

import twisted
import twisted.internet.protocol
import twisted.internet.reactor
import timer
import mq
import net.link as link
import conf

if "g_ConnectLink" not in globals():
	g_ConnectLink = []
if "g_AcceptLink" not in globals():
	g_AcceptLink = []

#-------------主动连接(作为客户端连接其他服务器)实例---------------
class DeferClient(twisted.internet.protocol.Protocol):

	def SetArgs(self, args):
		self.m_ServerID = args[0]
		self.m_Index = args[1]

	def connectionMade(self):
		global g_ConnectLink
		if self not in g_ConnectLink:
			g_ConnectLink.append(self)
		else:
			raise Exception("Net Error: link %d repeat"%(g_ConnectLink.index(self)))
		iID = g_ConnectLink.index(self)
		print("主动连接%s 已建立网络层连接"%iID)
		if not timer.GetTimer("SendMq_Handler"):
			timer.Call_out(DELAY_TIME, "SendMq_Handler", SendMq_Handler)

		PutData((SELF, SELF_LOCALMAP, (self.m_ServerID, self.m_Index)))
		d

	def dataReceived(self, data):
		iID = g_ConnectLink.index(self)
		PutData((C2S, iID, data))
		print("网络层接收到数据，并已加入消息队列")

	def connectionLost(self, reason):
		global g_ConnectLink
		print("与服务器断开连接")
		iID = 0
		if self in g_ConnectLink:
			iID = g_ConnectLink.index(self)
			g_ConnectLink.remove(self)

		PutData((SELF, iID, "connecteddisconnect"))

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
		global g_AcceptLink
		if self not in g_AcceptLink:
			g_AcceptLink.append(self)
		else:
			raise Exception("Net Error: link %d repeat"%(g_AcceptLink.index(self)))
		iID = g_AcceptLink.index(self)
		print("主动连接%s 已建立网络层连接"%iID)
		if not timer.GetTimer("SendMq_Handler"):
			timer.Call_out(DELAY_TIME, "SendMq_Handler", SendMq_Handler)

	def connectionLost(self, reason):
		global g_AcceptLink
		print("与服务器断开连接")
		iID = 0
		if self in g_AcceptLink:
			iID = g_ConnectLink.index(self)
			g_AcceptLink.remove(self)

		PutData((SELF, iID, "accepteddisconnect"))

	def dataReceived(self, data):
		iID = g_ConnectLink.index(self)
		PutData((S2S, iID, data))
		print("【C2S】收到客户端数据，并已加入消息队列")

class CBaseServerFactory(twisted.internet.protocol.Factory):
	protocol = CServer

def run(oSendMq, oRecvMq, oConfInitFunc):
	oConfInitFunc()
	link.Init()

	mq.SetMq(oSendMq, MSGQUEUE_SEND)
	mq.SetMq(oRecvMq, MSGQUEUE_RECV)

	lstConfigs = conf.GetConnects()
	for tConfig in lstConfigs:
		iServerID, dConfig = tConfig
		sIP = dConfig["sIP"]
		iPort = dConfig["iPort"]
		index = dConfig["iIndex"]
		twisted.internet.reactor.connectTCP(sIP, iPort, DefaultClientFactory())
	# twisted.internet.reactor.listenTCP(CSERVER_PORT, CBaseServerFactory())
	twisted.internet.reactor.listenTCP(SSERVER_PORT, CBaseServerFactory())
	print("服务端启动完毕，等待客户端连接")
	twisted.internet.reactor.run()

def SendMq_Handler():
	HANDLE_MAX = 100
	oMq = mq.GetMq(MSGQUEUE_SEND)
	if oMq.empty():
		timer.Call_out(DELAY_TIME, "SendMq_Handler", SendMq_Handler)
		return
	iHandled = 0
	while not oMq.empty() and iHandled <= HANDLE_MAX:
		iHandled += 1
		tData = oMq.get()
		iType, iLink, bData = tData
		print("消息队列数据准备发送至客户端 %s" % bData)
		oLink = CallManagerFunc("link", "GetLink", iLink, iType)
		oLink.m_Socket.transport.getHandle().sendall(bData)
	timer.Call_out(DELAY_TIME, "SendMq_Handler", SendMq_Handler)

def PutData(data):
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	if oRecvMq:
		if oRecvMq.full():
			print("数据在加载")
			return
		oRecvMq.put(data)
		print("网络层接收到数据，并已加入消息队列")

def S2SIdentify(oProto, iServer, iIndex):
	oPacketPrepare = PacketPrepare(SS_IDENTIFY)
	PacketAddI(iServer, oPacketPrepare)
	PacketAddI(iIndex, oPacketPrepare)
	bData = oPacketPrepare.m_BytesBuffer
	oProto.transport.getHandle().sendall(bData)