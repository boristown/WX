# -*- coding: utf-8 -*-
# filename: Console.py

import profile
import ZeroAI
import sys

def run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

while True:
  print ('input :')
  value = sys.stdin.readline()
  print (ZeroAI.chat(value))
  #print (run(ZeroAI.chat(value)))
  #profile.run("ZeroAI.chat(value)")
