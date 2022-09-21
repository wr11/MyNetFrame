# -*- coding: utf-8 -*-

from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV

import multiprocessing
import script
import net
import mq
import sys
import conf

if __name__ == "__main__":
	iServerID, iIndex = sys.argv[1], sys.argv[2]

	conf.Init(int(iServerID), int(iIndex))
	mq.Init()

	oSendMq = mq.GetMq(MSGQUEUE_SEND)
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	oProcessScript = multiprocessing.Process(target = script.main, args=(oSendMq, oRecvMq, ))
	oProcessNet = multiprocessing.Process(target = net.main, args=(oSendMq, oRecvMq, ))

	oProcessScript.start()
	oProcessNet.start()