# -*- coding: utf-8 -*-
from pubdefines import MSGQUEUE_SEND

import struct
import net.clientlink as clientlink
import mq

def NetPackagePrepare(byteContent = b""):
	return CNetPackage(byteContent)

class CNetPackage:
	def __init__(self, byteContent):
		self.m_BytesBuffer = byteContent
		self.m_Offset = 0

	def PackInto(self, byteContent):
		self.m_BytesBuffer += byteContent

	def Unpack(self, sType):
		iAddOffset = struct.calcsize(sType)
		byteContent = self.m_BytesBuffer[self.m_Offset:self.m_Offset+iAddOffset]
		self.m_Offset += iAddOffset
		return struct.unpack(sType, byteContent)[0]

	def UnpackEnd(self):
		return self.m_BytesBuffer[self.m_Offset:]

def PacketPrepare(header):
	oNetPack = NetPackagePrepare()
	PacketAddInt16(header, oNetPack)
	return oNetPack

def PacketAddInt(iVal, oNetPack):
	if iVal <= 255:
		PacketAddInt8(1, oNetPack)
		PacketAddInt8(iVal, oNetPack)
	elif 255 < iVal <= 65535:
		PacketAddInt8(2, oNetPack)
		PacketAddInt16(iVal, oNetPack)
	elif 65535 < iVal <= 4294967295:
		PacketAddInt8(4, oNetPack)
		PacketAddInt32(iVal, oNetPack)
	elif 4294967296 < iVal <= 9223372036854775807:
		PacketAddInt8(8, oNetPack)
		PacketAddInt64(iVal, oNetPack)
	else:
		PrintError("protocol error: python int value bigger than int64 %s"%(iVal))

def PacketAddInt8(iVal, oNetPack):
	"""
	无符号1字节整形 0-255
	"""
	if not isinstance(iVal, int):
		iVal = int(iVal)
	byteData = struct.pack("B", iVal)
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddInt16(iVal, oNetPack):
	"""
	无符号2字节整形 0-65535
	"""
	if not isinstance(iVal, int):
		iVal = int(iVal)
	byteData = struct.pack("H", iVal)
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddInt32(iVal, oNetPack):
	"""
	无符号4字节整形 0-4294967295
	"""
	if not isinstance(iVal, int):
		iVal = int(iVal)
	byteData = struct.pack("I", iVal)
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddInt64(iVal, oNetPack):
	"""
	无符号8字节整形 0-9223372036854775807 尽量少的使用，长整形可以转成字符串进行压包
	"""
	if not isinstance(iVal, int):
		iVal = int(iVal)
	byteData = struct.pack("Q", iVal)
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddB(bytes, oNetPack):
	oNetPack.PackInto(bytes)

def PacketAddC(char, oNetPack):
	byteData = struct.pack('c', bytes(char.encode("utf-8")))
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddS(sVal, oNetPack):
	"""
	默认最长4294967295,8字节的长度最好不要用，需要限制字符串长度
	"""
	sEncodeStr = sVal.encode('utf-8')
	iLen = len(sEncodeStr)
	PacketAddInt(iLen, oNetPack)
	if iLen == 1:
		PacketAddC(sEncodeStr, oNetPack)
	else:
		byteData = struct.pack('%ss' % len(sEncodeStr), sEncodeStr)
		if byteData:
			oNetPack.PackInto(byteData)

def PacketAddBool(bool, oNetPack):
	iVal = 0
	if bool:
		iVal = 1
	PacketAddInt8(iVal, oNetPack)

def PacketSend(oNetPack):
	oMq = mq.GetMq(MSGQUEUE_SEND)
	bData = oNetPack.m_BytesBuffer
	if oMq:
		if oMq.full():
			print("网络延迟中")
			return
		oMq.put(bData)
		print("数据 %s 已加入消息队列" % (bData))
	del oNetPack

'''def PacketSend(oNetPack):
	oLink = clientlink.GetLink()
	if oLink and oLink.m_Socket:
		print("数据 %s 打包完毕，发送至服务端" % (oNetPack.m_BytesBuffer))
		oLink.m_Socket.transport.write(oNetPack.m_BytesBuffer)
	del oNetPack'''

def UnpackPrepare(byteData):
	oNetPackage = NetPackagePrepare(byteData)
	return oNetPackage

def UnpackInt(oNetPackage):
	iByte = UnpackInt8(oNetPackage)
	if iByte == 1:
		return UnpackInt8(oNetPackage)
	elif iByte == 2:
		return UnpackInt16(oNetPackage)
	elif iByte == 4:
		return UnpackInt32(oNetPackage)
	elif iByte == 8:
		return UnpackInt64(oNetPackage)
	else:
		PrintError("netpackage error: unpack int bigger than int64")

def UnpackInt8(oNetPackage):
	"""
	无符号1字节整形 0-255
	"""
	return int(oNetPackage.Unpack("B"))

def UnpackInt16(oNetPackage):
	"""
	无符号2字节整形 0-65535
	"""
	return int(oNetPackage.Unpack("H"))

def UnpackInt32(oNetPackage):
	"""
	无符号4字节整形 0-4294967295
	"""
	return int(oNetPackage.Unpack("I"))

def UnpackInt64(oNetPackage):
	"""
	无符号8字节整形 0-9223372036854775807 尽量少的使用，长整形可以转成字符串进行压包
	"""
	return int(oNetPackage.Unpack("Q"))

def UnpackBool(oNetPackage):
	iVal = UnpackInt8(oNetPackage)
	bVal = False
	if iVal:
		bVal = True
	return bVal

def UnpackC(oNetPackage):
	return oNetPackage.Unpack("c").decode("utf-8")

def UnpackEnd(oNetPackage):
	return oNetPackage.UnpackEnd()

def UnpackS(oNetPackage):
	"""
	默认最长4294967295字节，需要限制字符串长度
	"""
	iLen = UnpackInt(oNetPackage)
	if iLen == 1:
		return UnpackC(oNetPackage)
	else:
		return oNetPackage.Unpack("%ss" % iLen).decode("utf-8")


"""
Format	C Type				Python type			Standard size	Notes
x		pad byte			no value	 	 
c		char				string of length 1	1	 
b		signed char			integer				1				(3)
B		unsigned char		integer				1				(3)
?		_Bool				bool				1				(1)
h		short				integer				2				(3)
H		unsigned short		integer				2				(3)
i		int					integer				4				(3)
I		unsigned int		integer				4				(3)
l		long				integer				4				(3)
L		unsigned long		integer				4				(3)
q		long long			integer				8				(2), (3)
Q		unsigned long long	integer				8				(2), (3)
f		float				float				4				(4)
d		double				float				8				(4)
s		char[]				string				1	 
p		char[]				string	 	 
P		void *				integer	 							(5), (3)

str.encode(‘utf-8')
bytes.decode(‘utf-8')
"""