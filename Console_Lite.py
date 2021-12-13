# -*- coding: utf-8 -*-
# filename: Console.py

import profile
import sys

def run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

while True:
  print ('input :')
  value = sys.stdin.readline()
  print(value)