# -*- coding: utf-8 -*-

class _const:
	class ConstError(TypeError):pass

	def __setattr__(self, name, value):
		if self.__dict__.has_key(name):
			raise self.ConstError("Const %s Can't be reassigned" %name)
		self.__dict__[name]=value

# import sys
# sys.modules[__name__] = _const()