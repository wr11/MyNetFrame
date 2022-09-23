# -*- coding: utf-8 -*-

import pubdefines

if "g_ClientNum" not in globals():
	g_ClientNum = 0

def Init():
	oLinkManager = CLinkManager()
	if not pubdefines.GetGlobalManager("link"):
		pubdefines.SetGlobalManager("link", oLinkManager)

class CLinkManager:
	def __init__(self):
		self.m_LinkDict = {}

	def AddLink(self, sHost, iPort, iServer, iIndex):
		tFlag = (iServer, iIndex)
		if tFlag not in self.m_LinkDict:
			self.m_LinkDict[tFlag] = (sHost, iPort)
		else:
			print("WARNING: link repeated %s %s %s %s"%(sHost, iPort, iServer, iIndex))

	def DelLink(self, iServer, iIndex):
		tFlag = (iServer, iIndex)
		if tFlag in self.m_LinkDict:
			del self.m_LinkDict[tFlag]

	def GetLink(self, iServer, iIndex):
		tFlag = (iServer, iIndex)
		return self.m_LinkDict.get(tFlag, ())