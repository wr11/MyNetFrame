# -*- coding: utf-8 -*-
import Limit_Function


@Limit_Function.Limit()
def A():
	print("A is called")
Limit_Function.a = A
Limit_Function.a()
def B():
	print("B is called")

Limit_Function.a = B