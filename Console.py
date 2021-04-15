# -*- coding: utf-8 -*-
# filename: Console.py

import profile
import ZeroAI
import sys

while True:
  print ('input :')
  value = sys.stdin.readline()
  print (ZeroAI.chat(value))
  #profile.run("ZeroAI.chat(value)")
