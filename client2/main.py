# -*- coding: utf-8 -*-

from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV

import multiprocessing
import mq
import script
import net

if __name__ == "__main__":
	mq.Init()

	oSendMq = mq.GetMq(MSGQUEUE_SEND)
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	oProcessNet = multiprocessing.Process(target = net.main, args=(oSendMq, oRecvMq, ))

	oProcessNet.start()
	script.main(oSendMq, oRecvMq)