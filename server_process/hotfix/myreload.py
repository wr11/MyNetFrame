# -*- coding: utf-8 -*-

import conf
import timer

if "FILE_LIST" not in globals():
	 FILE_LIST = []

def Init():
	if not conf.IsDebug():
		return
	LookFile()
	PrintDebug("reload inited", FILE_LIST)
	timer.Call_out(5, "ProjReload", MyReload)

def MyReload():
	PrintNotify("reloading ... ")
	LookFile(True, True)
	timer.Call_out(5, "ProjReload", MyReload)

def LookFile(bReload = False, bNotifyNew = False):
	import os
	sCurPath = os.getcwd()
	sCurPath = "%s\server_process"%(sCurPath)
	lstFile = os.listdir(sCurPath)
	for sName in lstFile:
		ReloadPyFile(sCurPath, sName, bReload, bNotifyNew)

def ReloadPyFile(sCurPath, sName, bReload, bNotifyNew):
	import os
	import importlib
	global FILE_LIST
	if sName.endswith(".py"):
		bNew = False
		if sName not in FILE_LIST:
			bNew = True
			FILE_LIST.append(sName)
		if bReload:
			from importlib import reload
			sMod = sName.split(".")[0]
			obj = importlib.import_module(sMod)
			if bNotifyNew and bNew:
				PrintNotify("new file is reloading %s ..."%(sMod))
			reload(obj)
			func = getattr(obj, "OnReload", None)
			if func:
				func()
	elif "." not in sName:
		import sys
		sCurPath = sCurPath + "\%s"%sName
		sys.path.append(sCurPath)
		lstFile = os.listdir(sCurPath)
		for sFile in lstFile:
			ReloadPyFile(sCurPath, sFile, bReload, bNotifyNew)